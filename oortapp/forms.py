from django import forms
from .models import FileUploadModel, FileGroup
from django.utils.translation import gettext_lazy as _


##################################
# File Uploads 
##################################
class UploadFileForm(forms.ModelForm):
    class Meta: 
        model = FileUploadModel
        fields = ('filename', 'upload', 'private')
        exclude = ['uploaded_at']        # this should be auto generated 

        labels = {
            'filename': _('Remote File Name'),
        }

##################################
# Folder Creation 
##################################
class FileGroupForm(forms.ModelForm):
    class Meta: 
        model = FileGroup
        fields = ('groupname', 'private')
        exclude = ['creation_date']        # this should be auto generated 

        labels = {
            'groupname': _('Folder Name'),
        }
