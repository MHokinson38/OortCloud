from django.shortcuts import render, redirect
from .models import FileUploadModel
# File Uploads 
from django.http import HttpResponseRedirect
from .forms import UploadFileForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user
from django.contrib import messages


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
    files = FileUploadModel.objects.filter(in_trash=False)
    return render(request, "home.html", {
        'files': files,
        'page_title': "Home"
    })


####################
# Trashed Files Page
####################
@login_required(login_url='login')
def trash(request):
    files = FileUploadModel.objects.filter(in_trash=True)
    return render(request, "home.html", {
        'files': files,
        'page_title': "Trash"
    })


####################
# File Upload Page 
####################
@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # File is saved
            return HttpResponseRedirect('/home')  # TODO: Create success url/alert
    else:
        form = UploadFileForm()

    return render(request, 'upload.html',
                  {'form': form
                   }
                  )
