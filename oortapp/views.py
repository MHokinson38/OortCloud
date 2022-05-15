from django.shortcuts import render, redirect
from .models import FileUploadModel, FileGroup
import logging

# File Uploads 
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UploadFileForm, FileGroupForm

# Downloads 
from zipfile import ZipFile

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from django.contrib import messages
import os
from django.conf import settings

@unauthenticated_user
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect')
    context = {}
    return render(request, 'login.html', context)

@unauthenticated_user
def create_user(request):
    if request.method == 'POST':
        f = UserCreationForm(request.POST)
        if f.is_valid():
            f.save()

            messages.success(request, 'Account created successfully')
            return redirect('home')
        else:
            for msg_key in f.error_messages:
                messages.info(request, f.error_messages[msg_key])

    else:
        f = UserCreationForm()

    return render(request, 'sign_up.html', {'form': f})


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')


####################
# Landing Page 
# [TODO: Move file fetching to another file]
####################
def fetchFiles(user, trash=False):
    public_files = FileUploadModel.objects.filter(in_trash=trash, private=False)
    private_files = FileUploadModel.objects.filter(in_trash=trash, private=True, owner=(user))

    return public_files | private_files

def fetchFolders(user, trash=False, exclude=None):
    public_folders = FileGroup.objects.filter(in_trash=trash, private=False)
    private_folders = FileGroup.objects.filter(in_trash=trash, private=True, owner=(user))

    return public_folders | private_folders

@login_required(login_url='login')
def home(request):
    files = fetchFiles(request.user)
    folders = fetchFolders(request.user)

    return render(request, "home.html", {
        'files': files,
        'folders': folders,
        'folders_dropdown': folders,
        'page_title': "Home"
    })


####################
# Trashed Files Page
####################
@login_required(login_url='login')
def trash(request):
    files = fetchFiles(request.user, trash=True)
    
    return render(request, "home.html", {
        'files': files,
        # 'folders': folders,
        'page_title': "Trash"
    })

####################
# Open Folder Page
####################
@login_required(login_url='login')
def open_folder(request, folder_id):
    
    try:
        folder = FileGroup.objects.get(id=folder_id)
        public_files = FileUploadModel.objects.filter(in_trash=False, private=False, file_group=folder)
        private_files = FileUploadModel.objects.filter(in_trash=False, private=True, owner=(request.user), file_group=folder)

        files = public_files | private_files
        
        public_folders = FileGroup.objects.filter(in_trash=False, private=False).exclude(id=folder_id)
        private_folders = FileGroup.objects.filter(in_trash=False, private=True, owner=(request.user)).exclude(id=folder_id)

        folders = public_folders | private_folders

    except FileGroup.DoesNotExist:
        return redirect('home')

    return render(request, "home.html", {
        'files': files,
        'folders_dropdown': folders,
        'page_title': folder.groupname
    })


####################
# File Upload Page 
####################
@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST':
        logging.debug("POST Request in the file upload")

        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            logging.debug("Success in uploading the file")
            
            # add owner to form data
            form_instance = form.save(commit=False)
            form_instance.owner = request.user
            form_instance.size = form.cleaned_data['upload'].size
            form_instance.save() # File is saved

            messages.success(request, 'File uploaded!')
            return HttpResponseRedirect('home')
    else:
        form = UploadFileForm()
    
    return render(request, 'upload.html', 
    {
        'form': form
    })

####################
# File backend 
# [TODO: Move this elsewhere]
####################
# Checks file permissions 
def has_permission(request, file, delete_op=False):
    if delete_op and file.owner == 3:
        return False
    return file.owner == request.user or file.owner == None or file.private == False


####################
# Download File 
####################
# TODO: Move this to another file 
# Downloads a single file for the user, returns (ret_code, http response)
# Return codes: 0: Success, return given http response, 1: error, redirect home
def download_single_file(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.upload.name)
    if os.path.exists(file_path):
        # download file
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/octet-stream')
            # Writing display name over uplaod name, should be clearer to user what they download
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file.filename)
            return (0, response)
    else:
        # file is gone from storage but not database
        file.delete()
        return (1, null) # redirect home

@login_required(login_url='login')
def download_file(request, file_id):
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if has_permission(request, file):
            ret_code, response = download_single_file(file)
            if ret_code == 0:
                return response
            else:
                messages.error(request, 'File not found!')
                return redirect('home')
        else:
            # permissions error message
            messages.warning(request, 'You do not have permission to download this file!')
            return redirect('home')
    
    except FileUploadModel.DoesNotExist:
        # file not found error message
        messages.error(request, 'File not found!')
        return redirect('home')

@login_required(login_url='login')
def download_folder(request, folder_id):
    logging.debug(f"downloading folder: {folder_id}")
    try:
        folder = FileGroup.objects.get(id=folder_id)
        files = FileUploadModel.objects.filter(file_group=folder)

        # Veify permissions exist on all files 
        permission_check = all(map(lambda file : has_permission(request, file), files))

        if not permission_check:
            logging.debug(f"User does not have permission for entire folder")
            # permissions error message
            messages.warning(request, 'You do not have permission to download this entire Folder!')
            return redirect('home')
        
        zfile_path = 'oort_download.zip'    # Write this somewhere else?
        with ZipFile(zfile_path, 'w') as z_file:
            for f in files:
                file_path = os.path.join(settings.MEDIA_ROOT, f.upload.name)
                
                logging.debug(f"Writing file: {file_path} into the zip file")
                # Writing files to zip archive, zip archive is going to have filenames rather than 
                # upload names to avoid confusion at download
                z_file.write(file_path, arcname=f.filename)     

        with open(zfile_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/octet-stream')
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(zfile_path)
            return response


    except FileGroup.DoesNotExist:
        # file not found error message
        messages.error(request, 'Folder not found!')
        return redirect('home')


####################
# Delete  
####################
# deletes file from table and storage 
# does not perform permission checks at this point, assumes permissions from user 
# Return codes: 0: redirect home, success. 1: redirect trash, success. 2: redirect home, failure
def remove_file(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.upload.name)
    if os.path.exists(file_path):
        # delete file
        if file.in_trash:
            # fully delete file
            os.remove(file_path)
            file.delete()
            return 1  
        else:
            # move file to trash
            file.in_trash = True
            file.save()
            return 0 

    else:
        # file is gone from storage but not database
        file.delete()
        return 2 

@login_required(login_url='login')
def delete_file(request, file_id):
    logging.debug(f"Deleting file: {file_id}")
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if has_permission(request, file, delete_op=True):
            ret_code = remove_file(file)
            if ret_code == 0:
                messages.success(request, "File moved to trash!")
                return redirect('home')
            if ret_code == 1:
                messages.success(request, "File permanently deleted!")
                return redirect('trash')
            if ret_code == 2:
                messages.warning(request, "File not found on disk!")    # not technically an error, operation can continue
                return redirect('home')
        else:
            # permissions error message
            messages.warning(request, 'You do not have permission to delete this file!')
            return redirect('home')
    
    except FileUploadModel.DoesNotExist:
        # file not found error message
        messages.error(request, 'File not found!')
        return redirect('home')

@login_required(login_url='login')
def delete_folder(request, folder_id):
    logging.debug(f"Deleting folder: {folder_id}")
    try:
        folder = FileGroup.objects.get(id=folder_id)
        files = FileUploadModel.objects.filter(file_group=folder)

        # Veify permissions exist on all files 
        permission_check = all(map(lambda file : has_permission(request, file, delete_op=True), files))

        if not permission_check:
            logging.debug(f"User does not have permission for entire folder")
            # permissions error message
            messages.warning(request, 'You do not have permission to delete this Folder because someone has private files in it!')
            return redirect('home')
        
        for f in files:
            # move files to root folder
            f.file_group = None
            f.save()
            if remove_file(f) == 2: # error occured 
                messages.warning(request, f"File {f.filename} was missing from disk. Operation finished anyway.")

        folder.delete()
        messages.success(request, 'Successfully deleted folder and moved files to trash!')
        return redirect('home')
        
    
    except FileGroup.DoesNotExist:
        # file not found error message
        messages.error(request, 'Folder not found!')
        return redirect('home')
    

####################
# Restore File 
####################
@login_required(login_url='login')
def restore_file(request, file_id):
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if file.owner == request.user or file.owner == None or file.private == False:
            # move file to trash
            file.in_trash = False
            file.save()
            messages.success(request, 'File moved out of trash!')
            return redirect('trash')
        else:
            # permissions error message
            messages.warning(request, 'You do not have permission to restore this file!')
            return redirect('trash')
    
    except FileUploadModel.DoesNotExist:
        # file not found error message
        messages.error(request, 'File not found!')
        return redirect('trash')

####################
# Folders  
####################
@login_required(login_url='login')
def create_folder(request):
    if request.method == 'POST':
        logging.debug("POST Request in the folder creation form")

        form = FileGroupForm(request.POST, request.FILES)
        if form.is_valid():
            logging.debug("Success in creating the folder")
            
            # add owner to form data
            form_instance = form.save(commit=False)
            form_instance.owner = request.user
            form_instance.save() # File is saved

            messages.success(request, 'Folder created!')
            return HttpResponseRedirect('home')
    else:
        form = FileGroupForm()
    
    return render(request, "new_folder.html", {
        'form': form
    })

@login_required(login_url='login')
def move_files(request):
    if request.method != 'POST':
        return redirect('home')
    
    folder_id = request.POST['folder_id']
    file_ids = request.POST.getlist('file_ids[]')

    logging.debug(f"{folder_id}, {file_ids}")
    if folder_id == '-1':
        folder = None
    else:
        folder = FileGroup.objects.get(id=folder_id)

    for fid in file_ids:
        file = FileUploadModel.objects.get(id=fid)
        file.file_group = folder

        file.save()

    messages.success(request, 'Files moved successfully!')
    return HttpResponse(200)