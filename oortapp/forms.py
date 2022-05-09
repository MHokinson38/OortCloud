from django import forms 
from .models import FileUploadModel

##################################
# File Uploads 
# [Refactor later if this file gets bloated]
##################################
class UploadFileForm(forms.Form):
    class Meta: 
        model = FileUploadModel
        fields = ['filename', 'file']
    