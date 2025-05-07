from django.shortcuts import render
from property_management.models import Property
from property_management.services import filter_properties
from django.shortcuts import redirect

def home(request):
    properties = Property.objects.all()
    recommended_properties = filter_properties(
        search_type='recommended',
        limit=3,
    )
    return render(request, 'home.html', {
        'properties': properties, 
        'recommended_properties': recommended_properties
    })

def set_language(request):
    language = request.GET.get('language', 'en')
    next_url = request.GET.get('next', '/')
    
    response = redirect(next_url)
    response.set_cookie('django_language', language)
    
 
    request.session['django_language'] = language
    return response