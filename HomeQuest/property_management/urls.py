from django.urls import path
from . import views

urlpatterns = [
    # Property management
    path('property_create/', views.create_property, name='property_create'),
    path('properties/', views.property_list, name='property_list'),
    path('properties/<int:property_id>/', views.property_detail, name='property_detail'),
    path('properties/<int:property_id>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:property_id>/delete/', views.property_delete, name='property_delete'),
    path('properties/<int:property_id>/verify/', views.property_verify, name='property_verify'),
    
    # User property interaction
    path('properties/search/', views.property_search, name='property_search'),
    path('properties/<int:property_id>/all/', views.property_detail_all, name='property_detail_all'),
    path('properties/for_sale/', views.properties_for_sale, name='properties_for_sale'),
    path('properties/for_rent/', views.properties_for_rent, name='properties_for_rent'),
    path('properties/recommended/', views.properties_recommended, name='properties_recommended'),
]