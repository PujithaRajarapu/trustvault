from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("upload/", views.upload, name="upload"),
    path("download/<int:doc_id>/", views.download, name="download"),
]