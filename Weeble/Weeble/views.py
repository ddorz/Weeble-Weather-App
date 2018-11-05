from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.contrib.auth.models import User
from Weeble.forms import SignUpForm
from Weeble.tokens import account_activation_token
from Weeble.models import Profile
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


@login_required(login_url='/login')
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
            user = form.save(commit=False)
            # Accounts active without confrimation until emails are sending
            # user.is_active = False
            user.save()

            user.profile.isPremium = form.cleaned_data.get('isPremium')
            user.profile.userName = form.cleaned_data.get('username')
            user.profile.password = pbkdf2(form.cleaned_data.get('password1'), 'salt')
            user.profile.email = form.cleaned_data.get('email')
            user.profile.registrationDate = datetime.datetime.today()
            user.profile.lastLoginDate = datetime.datetime.today()
            # Accounts set to active without confirming email until we have a domain/STMP server to send emails
            user.profile.emailConfirmed = True
            user.save()

            current_site = get_current_site(request)
            subject = 'Confirm your email to activate your Weeble Account'
            message = render_to_string('..\\templates\\account_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
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

            return redirect('account_activation_email_sent')
    else:
        form = SignUpForm()
    return render(request, '..\\templates\signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, '..\\templates\\account_activation_email_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_encode(uidb64))
        # Get django.contrib.auth.User object. This is the django auth_user table
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Set user object to active and save
        user.is_active = True

        user.save()

        # Get Profile object. This is from our 'users' table.
        # Update email confirmed field to true and save to db.
        user = Profile.objects.get(username=user.username)
        user.emailConfirmed = True
        user.save()

        login(request, user)
        return redirect('home')
    else:
        return render(request, '..\\templates\\account_activation_invalid_link.html')