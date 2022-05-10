from django import forms
from .models import FileUploadModel
from django.utils.translation import gettext_lazy as _


##################################
# File Uploads 
# [Refactor later if this file gets bloated]
##################################
class UploadFileForm(forms.ModelForm):
    class Meta: 
        model = FileUploadModel
        fields = ('filename', 'upload', 'private')
        exclude = ['uploaded_at']        # this should be auto generated 

        labels = {
            'filename': _('Remote File Name'),
        }
