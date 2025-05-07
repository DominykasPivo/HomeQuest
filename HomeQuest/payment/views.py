from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import SubscriptionPurchaseForm
from .payment_strategies import CardPayment, IBANPayment, PayPalPayment
from .models import PaymentProcessor
from notification_system.models import Notification
from subscription_management.services import get_or_create_gold_seller, update_subscription

# Subscription prices 
SUBSCRIPTION_PLANS = [
    ('weekly', 'Weekly - 15 EUR'),
    ('monthly', 'Monthly - 40 EUR'),
    ('quarterly', 'Quarterly - 60 EUR'),
    ('yearly', 'Yearly - 100 EUR'),
]

SUBSCRIPTION_PRICES = {
    'basic': 0,
    'weekly': 15,
    'monthly': 40,
    'quarterly': 60,
    'yearly': 100,
}

@login_required
def buy_gold_subscription(request):
    plans = SUBSCRIPTION_PLANS
    if request.method == 'POST':
        form = SubscriptionPurchaseForm(request.POST, plans=plans)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            selected_plan = form.cleaned_data['plan']
            amount = SUBSCRIPTION_PRICES[selected_plan]

            
            processor = PaymentProcessor()
            payment_kwargs = {}
            if payment_method == 'card':
                processor.set_strategy(CardPayment())
                payment_kwargs = {
                    'card_number': request.POST.get('card_number'),
                    'full_name': request.POST.get('card_full_name'),
                    'expiration_date': request.POST.get('expiration_date'),
                    'cvv': request.POST.get('cvv'),
                }
            elif payment_method == 'iban':
                processor.set_strategy(IBANPayment())
                payment_kwargs = {
                    'iban': request.POST.get('iban'),
                    'full_name': request.POST.get('iban_full_name'),
                    'bank_name': request.POST.get('bank_name'),
                    'bic': request.POST.get('bic'),
                }
            elif payment_method == 'paypal':
                processor.set_strategy(PayPalPayment())
                payment_kwargs = {
                    'paypal_email': request.POST.get('paypal_email'),
                    'paypal_password': request.POST.get('paypal_password'),
                }

            payment_success = processor.process_payment(amount, **payment_kwargs)
            if not payment_success:
                messages.error(request, "Payment failed. Please check your details and try again.")
                return render(request, 'buy_gold_subscription.html', {'form': form})

            
            gold_seller = get_or_create_gold_seller(request.user)
            update_subscription(gold_seller, 'buy_gold', selected_plan)

            Notification.objects.create(
                user=request.user,
                message=f"You have successfully purchased a Gold subscription ({gold_seller.get_subscription_type_display()})."
            )
            messages.success(request, "Your subscription has been updated!")
            return redirect('manage_subscription')
    else:
        form = SubscriptionPurchaseForm(plans=plans)
    return render(request, 'buy_gold_subscription.html', {'form': form})