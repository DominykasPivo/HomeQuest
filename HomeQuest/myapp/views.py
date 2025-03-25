from django.shortcuts import render, redirect, HttpResponse
from .models import UserInput

# Create your views here.
def home(request):
    return HttpResponse("Hello world!")

def input_form(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        UserInput.objects.create(text=user_input)
        return redirect('input_form')

    # Retrieve all UserInput entries
    user_inputs = UserInput.objects.all()
    context = {'user_inputs': user_inputs}
    return render(request, 'base.html', context)

