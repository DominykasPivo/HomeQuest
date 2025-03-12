from django.shortcuts import render, HttpResponse
from django.shortcuts import render, redirect
from .models import UserInput

# Create your views here.
def home(request):
    return HttpResponse("Hello world!")


def input_form(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        UserInput.objects.create(text=user_input)
        return redirect('input_form')
    return render(request, 'base.html')

