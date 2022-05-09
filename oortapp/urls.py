from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("home", views.home, name="home"),
    path("trash", views.trash, name="trash"),
    path("upload", views.upload_file, name="upload"),
    path("delete/<int:id>", views.home, name="delete"),
    path("download/<int:id>", views.home, name="download"),

    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout')
]