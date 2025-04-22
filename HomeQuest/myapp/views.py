from django.shortcuts import render, redirect, HttpResponse
from .models import UserInput #have to make user models
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .services import save_user_input, get_all_user_inputs
from .forms import UserRegistrationForm

# Create your views here.
def home(request):
    return render(request, 'base.html')

def input_form(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        UserInput.objects.create(text=user_input)
        return redirect('input_form')

    # Retrieve all UserInput entries
    user_inputs = get_all_user_inputs()
    context = {'user_inputs': user_inputs}
    return render(request, 'input.html', context)

def login_email_phone(request):
    return render(request, 'login_email_phone.html')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to login page after successful registration
        else:
            print(form.errors)  # Debugging: Print form errors to the console
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_email(request):
    return render(request, 'login_email.html')

def login_phone(request):
    return render(request, 'login_phone.html')




