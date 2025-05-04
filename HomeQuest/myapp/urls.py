from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    #user/profile interaction
    path('register/', views.register, name='register'),
    path('login/', views.login_email_phone, name='login'),
    path('login/email/', views.login_email, name='login_email'),
    path('login/phone/', views.login_phone, name='login_phone'),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout_view, name="logout"), 
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('2fa/', views.verify_2fa, name='verify_2fa'),
    # User subscription management
    path('manage_subscription/', views.manage_subscription, name='manage_subscription'),
    path('buy_gold_subscription/', views.buy_gold_subscription, name='buy_gold_subscription'),
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    # Property management
    path('property_create/', views.create_property, name='property_create'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:property_id>/', views.property_detail, name='property_detail'),
    path('properties/<int:property_id>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:property_id>/delete/', views.property_delete, name='property_delete'),
    path('properties/<int:property_id>/verify/', views.property_verify, name='property_verify'),
    #User property interaction
    path('properties/search/', views.property_search, name='property_search'),
    path('properties/<int:property_id>/all/', views.property_detail_all, name='property_detail_all'),
    path('properties/for_sale/', views.properties_for_sale, name='properties_for_sale'),
    path('properties/for_rent/', views.properties_for_rent, name='properties_for_rent'),
    path('properties/recommended/', views.properties_recommended, name='properties_recommended'),
]
