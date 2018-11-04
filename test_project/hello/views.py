from django.shortcuts import render
from django.http import HttpResponse

def faqView(request):
    return render(request, 'pages/faq.html')

def searchView(request):
    return render(request, 'pages/search.html')

def citysavedView(request):
    return render(request, 'pages/citysaved.html')

def logoutView(request):
    return render(request, 'pages/logout.html') 