from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


################################
# File Upload Model 
################################
# Generate unique file paths for each user in internal file system 
def user_directory_path(instance, filename):
    return f"user_{instance.owner}/{filename}"               # Add user filenaming later 


class FileGroup(models.Model):
    groupname = models.CharField(max_length=100)        # Display name 
    creation_date = models.DateTimeField(null=True, default=timezone.now)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    in_trash = models.BooleanField(default=False, null=False)
    private = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.groupname

class FileUploadModel(models.Model):
    # Giving upload to callback which takes two arguments, as seen above 
    # Look into storage argument, might be needed for database/displaying uploaded files 
    upload = models.FileField(upload_to=user_directory_path)

    # Display name (not name given to path generator)
    filename = models.CharField(max_length=100)     
    # Whether files are viewable by other users             
    private = models.BooleanField(default=False, null=False)
    
    # Auto-set fields 
    upload_date = models.DateTimeField(null=True, default=timezone.now)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    in_trash = models.BooleanField(default=False, null=False)
    size = models.IntegerField(null=False, default=0)
    file_group = models.ForeignKey(FileGroup, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.filename



