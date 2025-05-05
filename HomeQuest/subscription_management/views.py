from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from user_management.models import Seller
from .models import GoldSeller
from .services import auto_downgrade_if_expired, cancel_subscription
from notification_system.services import create_notification
from django.shortcuts import get_object_or_404

@login_required
def manage_subscription(request):
    seller = get_object_or_404(Seller, pk=request.user.pk)
    gold_seller = GoldSeller.objects.filter(pk=seller.pk).first()


    # Auto-downgrade if subscription expired
    if gold_seller:
        auto_downgrade_if_expired(gold_seller)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'cancel' and gold_seller and gold_seller.subscription_plan != 'basic':
            cancel_subscription(gold_seller)
            messages.success(request, "Your subscription has been cancelled. You are now on the Basic plan.")
            return redirect('manage_subscription')
        elif action == 'buy':
            return redirect('buy_gold_subscription')

    return render(request, 'manage_subscription.html', {'gold_seller': gold_seller})




