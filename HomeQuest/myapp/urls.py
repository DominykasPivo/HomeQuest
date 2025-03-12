from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path("input_form/", views.input_form, name="input_form"),
]
