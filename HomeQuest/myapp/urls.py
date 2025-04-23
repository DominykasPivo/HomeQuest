from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login_email_phone, name='login'),
    path('login/email/', views.login_email, name='login_email'),
    path('login/phone/', views.login_phone, name='login_phone'),
    path("input_form/", views.input_form, name="input_form"),
]
