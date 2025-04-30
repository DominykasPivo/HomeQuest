from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path('register/', views.register, name='register'),
    path('login/', views.login_email_phone, name='login'),
    path('login/email/', views.login_email, name='login_email'),
    path('login/phone/', views.login_phone, name='login_phone'),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout_view, name="logout"), 
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('manage_subscription/', views.manage_subscription, name='manage_subscription'),
    # Property management
    path('property_create/', views.create_property, name='property_create'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:property_id>/', views.property_detail, name='property_detail'),
    path('properties/<int:property_id>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:property_id>/delete/', views.property_delete, name='property_delete'),
    path('properties/<int:property_id>/verify/', views.property_verify, name='property_verify'),
    #User property interaction
    path('properties/search/', views.property_search, name='property_search'),

]
