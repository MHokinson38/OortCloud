from django.shortcuts import render, redirect
from .models import FileUploadModel
import logging

# File Uploads 
from django.http import HttpResponseRedirect, HttpResponse
from .forms import UploadFileForm

from django.contrib.auth import authenticate, login, logout
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


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')


####################
# Landing Page 
####################
@login_required(login_url='login')
def home(request):
    public_files = FileUploadModel.objects.filter(in_trash=False, private=False)
    private_files = FileUploadModel.objects.filter(in_trash=False, private=True, owner=(request.user))
    files = public_files | private_files
    return render(request, "home.html", {
        'files': files,
        'page_title': "Home"
    })


####################
# Trashed Files Page
####################
@login_required(login_url='login')
def trash(request):
    public_files = FileUploadModel.objects.filter(in_trash=True, private=False)
    private_files = FileUploadModel.objects.filter(in_trash=True, private=True, owner=(request.user))
    files = public_files | private_files
    return render(request, "home.html", {
        'files': files,
        'page_title': "Trash"
    })


####################
# File Upload Page 
####################
@login_required(login_url='login')
def upload_file(request):
    success = False
    if request.method == 'POST':
        logging.debug("POST Request in the file upload")

        form = UploadFileForm(request.POST, request.FILES)
        success = form.is_valid()
        
        if success:
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
        }
    )


####################
# Download File 
####################
@login_required(login_url='login')
def download_file(request, file_id):
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if file.owner == request.user or file.owner == None:
            file_path = os.path.join(settings.MEDIA_ROOT, file.upload.name)
            if os.path.exists(file_path):
                # download file
                with open(file_path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/octet-stream')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                    return response
            else:
                # file is gone from storage but not database
                file.delete()
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


####################
# Delete File 
####################
@login_required(login_url='login')
def delete_file(request, file_id):
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if file.owner == request.user or file.owner == None:
            file_path = os.path.join(settings.MEDIA_ROOT, file.upload.name)
            if os.path.exists(file_path):
                # delete file
                if file.in_trash:
                    # fully delete file
                    os.remove(file_path)
                    file.delete()
                    messages.success(request, 'File permanently deleted!')
                    return redirect('trash')
                else:
                    # move file to trash
                    file.in_trash = True
                    file.save()
                    messages.success(request, 'File moved to trash!')
                    return redirect('home')

            else:
                # file is gone from storage but not database
                file.delete()
                messages.error(request, 'File not found!')
                return redirect('home')
        else:
            # permissions error message
            messages.warning(request, 'You do not have permission to delete this file!')
            return redirect('home')
    
    except FileUploadModel.DoesNotExist:
        # file not found error message
        messages.error(request, 'File not found!')
        return redirect('home')
    

####################
# Restore File 
####################
@login_required(login_url='login')
def restore_file(request, file_id):
    try:
        file = FileUploadModel.objects.get(id=file_id)
        
        if file.owner == request.user or file.owner == None:
            # move file to trash
            file.in_trash = False
            file.save()
            messages.success(request, 'File moved out of trash!')
            return redirect('home')
        else:
            # permissions error message
            messages.warning(request, 'You do not have permission to restore this file!')
            return redirect('home')
    
    except FileUploadModel.DoesNotExist:
        # file not found error message
        messages.error(request, 'File not found!')
        return redirect('home')
