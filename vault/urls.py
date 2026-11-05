from django.urls import path
from . import views
from . import admin_views
from . import doc_views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("upload/", views.upload, name="upload"),
    path("download/<int:doc_id>/", views.download, name="download"),
    path("share/<int:doc_id>/", views.share, name="share"),
    path("revoke/<int:doc_id>/<int:user_id>/", views.revoke, name="revoke"),
    path("activity/", admin_views.activity, name="activity"),
    path("search/", views.search, name="search"),
    path("delete/<int:doc_id>/", doc_views.delete, name="delete"),
]