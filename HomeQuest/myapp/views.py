from django.shortcuts import render, redirect, HttpResponse
from .models import User, UserInput #have to make user models
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .services import save_user_input, get_all_user_inputs
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required

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
            user = form.save(commit=False)  # Don't save to the database yet
            user.set_password(form.cleaned_data['password'])  # Hash the password
            user.save()  # Save the user to the database
            return redirect('login')  # Redirect to the login page after successful registration
        else:
            print(form.errors)  # Debugging: Print form errors to the console
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            # Get the user by email
            user = User.objects.get(email=email)
            # Authenticate using the username (since Django uses username internally)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after login
            else:
                messages.error(request, 'Invalid email or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login_email.html')

def login_phone(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        try:
            user = User.objects.get(phone_number=phone_number)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to the home page after login
            else:
                messages.error(request, 'Invalid phone number or password.')
        except User.DoesNotExist:
            messages.error(request, 'Invalid phone number or password.')
    return render(request, 'login_phone.html')


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('login')

