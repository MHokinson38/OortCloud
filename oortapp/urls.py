from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("trash", views.trash, name="trash"),
    path("upload", views.upload_file, name="upload"),
    path("create_folder", views.create_folder, name="create_folder"),
    path("move_files", views.move_files, name="move_files"),
    path("delete/<int:file_id>", views.delete_file, name="delete"),
    path("delete_folder/<int:folder_id>", views.delete_folder, name="delete_folder"),
    path("restore/<int:file_id>", views.restore_file, name="restore"),
    path("download/<int:file_id>", views.download_file, name="download"),
    path("download_folder/<int:folder_id>", views.download_folder, name="download_folder"),
    path("open_folder/<int:folder_id>", views.open_folder, name="open_folder"),

    path('login', views.login_user, name='login'),
    path('sign_up', views.create_user, name='sign_up'),
    path('logout', views.logout_user, name='logout')
]