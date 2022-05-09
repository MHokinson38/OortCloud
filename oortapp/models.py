from django.db import models

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
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
