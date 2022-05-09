from django.shortcuts import render

import logging

# File Uploads 
from django.http import HttpResponseRedirect 
from .forms import UploadFileForm 

####################
# Landing Page 
####################
def home(request):
    return render(request, "base.html", {})

####################
# File Upload Page 
####################
def upload_file(request):
    success = False
    if request.method == 'POST':
        logging.debug("POST Request in the file upload")

        form = UploadFileForm(request.POST, request.FILES)
        success = form.is_valid()
        
        if success:
            logging.debug("Success in uploading the file")
            
            form.save()     # File is saved 
            return HttpResponseRedirect('/home') # TODO: Create success url/alert
    else:
        form = UploadFileForm()
    
    return render(request, 'upload.html', 
        {'form': form,
         'success': success
        }
    )

