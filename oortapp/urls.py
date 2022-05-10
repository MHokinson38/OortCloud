from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("trash", views.trash, name="trash"),
    path("upload", views.upload_file, name="upload"),
    path("create_folder", views.create_folder, name="create_folder"),
    path("delete/<int:file_id>", views.delete_file, name="delete"),
    path("restore/<int:file_id>", views.restore_file, name="restore"),
    path("download/<int:file_id>", views.download_file, name="download"),

    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout')
]