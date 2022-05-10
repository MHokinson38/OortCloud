from django.contrib import admin
from .models import FileUploadModel, FileGroup

# Register your models here.

admin.site.register(FileUploadModel)
admin.site.register(FileGroup)
