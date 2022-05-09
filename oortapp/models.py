from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


################################
# File Upload Model 
################################
# Generate unique file paths for each user in internal file system 
def user_directory_path(instance, filename):
    return f"user_{0}/{filename}"               # Add user filenaming later 


class FileUploadModel(models.Model):
    # Giving upload to callback which takes two arguments, as seen above 
    # Look into storage argument, might be needed for database/displaying uploaded files 
    upload = models.FileField(upload_to=user_directory_path)

    filename = models.CharField(max_length=100)                 # Display name (not name given to path generator)
    upload_date = models.DateTimeField(null=True, default=timezone.now)
    owner = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    in_trash = models.BooleanField(default=False, null=False)

    def __str__(self):
        return self.filename
