from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from two_factor.urls import urlpatterns as tf_urls
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('', include('user_management.urls')),
    path('', include('property_management.urls')),
    path('', include('payment.urls')),
    path('', include('notification_system.urls')),
    path('', include('subscription_management.urls')),
    path("", views.home, name="home"),
]

urlpatterns.extend([path('', include(tf_urls))])

#urlpatterns.append(path('', include("myapp.urls")))



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)