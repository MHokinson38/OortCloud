from django.shortcuts import render

# File Uploads 
from django.http import HttpResponseRedirect
from .forms import UploadFileForm


####################
# Landing Page 
####################
def home(request):
    # python prep
    return render(request, "home.html", {})


####################
# File Upload Page 
####################
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
