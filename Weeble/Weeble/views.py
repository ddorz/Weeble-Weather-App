from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from Weeble.forms import SignUpForm
from Weeble.models import User
from Weeble.models import FreeUser
from Weeble.models import PremiumUser
from Weeble.pbkdf2 import pbkdf2
import datetime
from django.contrib.auth.forms import UserCreationForm
from geopy.geocoders import Nominatim
import certifi
import ssl
import geopy.geocoders
import time
import requests


@login_required
def home(request):
    return render(request, '..\\templates\home.html')


# Returns the index.html template
def index(request):
    # Pass custom ssl context so geopy will accept requests
    #ctx = ssl.create_default_context(cafile=certifi.where())
    #geopy.geocoders.options.default_ssl_context = ctx

    # Geoencode city 'Tampa'
    #geolocator = Nominatim(user_agent="Weeble")
    #location = geolocator.geocode("Tampa")

    # Build and send DarkSky request -- Replace secret key 'e49ed24b0e86f5466d6dde252a31addd' with your DarkSky API key
    #url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(location.latitude) + ", " + str(location.longitude)
    #city_weather = requests.get(url).json()

    # Print weather data
    #print(city_weather)

    return render(request, '..\\templates\weeble\index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            user = User.objects.create(userId=None,
                                       isPremium=form.cleaned_data.get('isPremium'),
                                       userName=form.cleaned_data.get('username'),
                                       password=pbkdf2(form.cleaned_data.get('password1'), 'salt'),
                                       email=form.cleaned_data.get('email'),
                                       registrationDate=None,
                                       lastLoginDate=datetime.date.today())

            user.save()

            raw_password = form.cleaned_data.get('password1')
            username = form.cleaned_data.get('username')

            if form.cleaned_data.get('isPremium'):
                premiumuser = PremiumUser.objects.create(userName=username,
                                                         premiumUserId=None,
                                                         firstCity=None,
                                                         secondCity=None,
                                                         thirdCity=None,
                                                         appCalls=0,
                                                         lastResetDate=None)
                premiumuser.save()
            else:
                freeuser = FreeUser.objects.create(userName=username,
                                                   freeUserId=None,
                                                   firstCity=None,
                                                   appCalls=0,
                                                   lastResetDate=None)
                freeuser.save()

            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, '..\\templates\signup.html', {'form': form})