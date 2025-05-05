from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_email_phone, name='login'),
    path('login/email/', views.login_email, name='login_email'),
    path('login/phone/', views.login_phone, name='login_phone'),
    path('2fa/', views.verify_2fa, name='verify_2fa'),
    path('logout/', views.logout_view, name='logout'),
]