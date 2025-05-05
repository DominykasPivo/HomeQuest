from django.urls import path
from . import views

urlpatterns = [
    path('buy_gold_subscription/', views.buy_gold_subscription, name='buy_gold_subscription'),
]