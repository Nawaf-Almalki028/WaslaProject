from django.shortcuts import render
from django.http import HttpResponse

def home_view(request):
    return render(request, 'main/auth.html', {
        'title': 'WASLA - Hackathon Platform'
    })

def about_view(request):
    
    return render(request, 'main/about.html', {'title': 'About WASLA'})

def contact_view(request):
    
    return render(request, 'main/contact.html', {
        'title': 'Contact Us'
    })

def hackathons_list(request):

    return render(request, 'main/hackathons.html', {
        'title': 'Hackathons'
    })

def pricing_view(request):
    
    return render(request, 'main/pricing.html', {'title': 'Pricing'})

def error_404(request, exception):
   
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    
    return render(request, 'errors/500.html', status=500)