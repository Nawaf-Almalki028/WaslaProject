from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.


def home_view(request:HttpRequest):


    return render(request, 'main/home.html' )


def base_view(request:HttpRequest):


    return render(request, 'main/base.html' )

