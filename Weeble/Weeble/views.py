from django.shortcuts import render

# Returns the index.html template
def index(request):
    return render(request, '..\\templates\weeble\index.html')