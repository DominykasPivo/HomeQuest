from django.urls import path
from . import views

urlpatterns = [
    path('manage_subscription/', views.manage_subscription, name='manage_subscription'),
]