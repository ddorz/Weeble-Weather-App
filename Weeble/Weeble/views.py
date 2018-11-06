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
from Weeble.forms import CityFormFreeUser, CityFormPremiumUser
from Weeble.forms import SignUpForm
from Weeble.tokens import account_activation_token
from Weeble.models import Profile
from Weeble.models import FreeUser
from Weeble.models import PremiumUser
from Weeble.pbkdf2 import pbkdf2
import Weeble.darkskyparser as Parser
import datetime
from django.contrib.auth.forms import UserCreationForm
from geopy.geocoders import Nominatim
import certifi
import ssl
import geopy.geocoders
import time
import requests
import pprint

DAILY_API_CALLS_FREE_USERS = 25
DAILY_API_CALLS_PREMIUM_USERS = 66


@login_required(login_url='/login')
def home(request):
    # Pass custom ssl context so geopy will accept requests
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    # Initialize geopy
    geolocator = Nominatim(user_agent="Weeble")

    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        puser = PremiumUser.objects.get(userName=profile.userName)
        apiCalls = puser.get_app_calls() if puser.appCalls is not None else 0
        cities = []
        weather_data = []

        # See if the user has exceeded daily API calls
        if apiCalls > DAILY_API_CALLS_PREMIUM_USERS:
            # Calculate the time between users last reset and now
            # d = (x minutes, y seconds)
            elapsed_time = datetime.datetime.now() - puser.get_last_reset_date()
            d = divmod(elapsed_time.total_seconds(), 60)
            # Divide the number of minutes by 60 minutes/hour * 24 hours/day => d / 1440
            # If at least 1 day (24 hours) has passed since the users last reset, reset their api calls and update db
            # Otherwise, redirect to error page
            if (d[0] / 1440) >= 1:
                puser.appCalls = 0
                puser.lastResetDate = datetime.datetime.now()
                puser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # Build list of user's cities saved in databaase
        for c in [puser.firstCity, puser.secondCity, puser.thirdCity]:
            if c is not None:
                cities.append(c)

        # True when user select 'Add City' button
        if request.method == 'POST':
            # Get form data
            form = CityFormPremiumUser(request.POST)
            if form.is_valid():
                # New city name and number of city to replace (1, 2, or 3)
                city = form.cleaned_data.get('city')
                city_number = form.cleaned_data.get('city_number')
                # Update first, second, or third city based on input
                if city_number == 1:
                    puser.firstCity = form.cleaned_data.get('city')
                    if len(cities) < 1:
                        cities.append(city)
                    else:
                        cities[0] = city
                elif city_number == 2:
                    puser.secondCity = form.cleaned_data.get('city')
                    if len(cities) < 2:
                        cities.append(city)
                    else:
                        cities[1] = city
                else:
                    puser.thirdCity = form.cleaned_data.get('city')
                    if len(cities) < 3:
                        cities.append(city)
                    else:
                        cities[2] = city

        form = CityFormPremiumUser()
        columnoffset = 0

        # Iterate over the user's cities, request forecast data from DarkSky API, then display them
        if cities is not None:
            for city in cities:
                location = geolocator.geocode(city)
                url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                    location.latitude) + ", " + str(location.longitude)
                darkskyjson = requests.get(url).json()
                weather = Parser.get_current_weather_basic(darkskyjson, city)
                weather_data.append(weather)
                columnoffset = columnoffset + 4
                apiCalls = apiCalls + 1

        # Update number of API calls made by user, save to database
        puser.appCalls = apiCalls
        puser.save()
        context = {"weather_data": weather_data, "form": form, "cities": cities}
        return render(request, '..\\templates\premiumuser_home.html', context)
    else:
        # Get FreeUser object corresponding to username of logged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        # Get number of API calls made by user
        apiCalls = fuser.get_app_calls() if fuser.appCalls is not None else 0

        # See if the user has exceeded daily API calls
        if apiCalls > DAILY_API_CALLS_FREE_USERS:
            # Calculate the time between users last reset and now
            # d = (x minutes, y seconds)
            elapsed_time = datetime.datetime.now() - fuser.get_last_reset_date()
            d = divmod(elapsed_time.total_seconds(), 60)
            # Divide the number of minutes by 60 minutes/hour * 24 hours/day => d / 1440
            # If at least 1 day (24 hours) has passed since the users last reset, reset their api calls and update db
            # Otherwise, redirect to error page
            if (d[0] / 1440) >= 1:
                fuser.appCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        cities = []
        weather_data = []

        for c in [fuser.firstCity]:
            if c is not None:
                cities.append(c)

        # True when user selects 'Add City' button
        if request.method == 'POST':
            form = CityFormFreeUser(request.POST)
            if form.is_valid():
                # Update the user's saved city
                fuser.firstCity = form.cleaned_data.get('city')
                # Request forecast data for city from DarkSky API
                location = geolocator.geocode(fuser.firstCity)
                url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                    location.latitude) + ", " + str(location.longitude)
                darkskyjson = requests.get(url).json()
                # Parse DarkSky data, update number of api calls made
                weather = Parser.get_current_weather_basic(darkskyjson, fuser.firstCity)
                weather_data.append(weather)
                apiCalls = apiCalls + 1
                cities = []

        form = CityFormFreeUser()

        if cities is not None:
            for city in cities:
                location = geolocator.geocode(city)
                url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                    location.latitude) + ", " + str(location.longitude)
                darkskyjson = requests.get(url).json()
                weather = Parser.get_current_weather_basic(darkskyjson, city)
                weather_data.append(weather)
                apiCalls = apiCalls + 1

        # Update number of api calls made by user, save free user data to database
        fuser.appCalls = apiCalls
        fuser.save()
        context = {"weather_data": weather_data, "form": form, "cities": cities}
        return render(request, '..\\templates\\freeuser_home.html', context)


@login_required(login_url='/login')
def weekly_weather(request):
    # Pass custom ssl context so geopy will accept requests
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    # Initialize geopy
    geolocator = Nominatim(user_agent="Weeble")

    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        return render(request, '..\\templates\errorNoAPICalls.html')
    else:
        # Get FreeUser object corresponding to username of logged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        # Get number of API calls made by user
        apiCalls = fuser.get_app_calls() if fuser.appCalls is not None else 0

        # See if the user has exceeded daily API calls
        if apiCalls > DAILY_API_CALLS_FREE_USERS:
            # Calculate the time between users last reset and now
            # d = (x minutes, y seconds)
            elapsed_time = datetime.datetime.now() - fuser.get_last_reset_date()
            d = divmod(elapsed_time.total_seconds(), 60)
            # Divide the number of minutes by 60 minutes/hour * 24 hours/day => d / 1440
            # If at least 1 day (24 hours) has passed since the users last reset, reset their api calls and update db
            # Otherwise, redirect to error page
            if (d[0] / 1440) >= 1:
                fuser.appCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        weather_data = []
        daily_data = []

        if fuser.firstCity is not None:
            location = geolocator.geocode(fuser.firstCity)
            url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                location.latitude) + ", " + str(location.longitude)
            darkskyjson = requests.get(url).json()
            # Parse DarkSky data, update number of api calls made
            weather_data = Parser.get_week_weather_basic(darkskyjson, fuser.firstCity)
            apiCalls = apiCalls + 1

        # Update number of api calls made by user, save free user data to database
        fuser.appCalls = apiCalls
        fuser.save()
        context = {"weather_data": weather_data}
        return render(request, '..\\templates\\freeuser_weekly_weather.html', context)


@login_required(login_url='/login')
def daily_weather(request):
    # Pass custom ssl context so geopy will accept requests
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx

    # Initialize geopy
    geolocator = Nominatim(user_agent="Weeble")

    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        puser = PremiumUser.objects.get(userName=profile.userName)
        apiCalls = puser.get_app_calls() if puser.appCalls is not None else 0
        cities = []
        weather_data_list = []

        # See if the user has exceeded daily API calls
        if apiCalls > DAILY_API_CALLS_PREMIUM_USERS:
            # Calculate the time between users last reset and now
            # d = (x minutes, y seconds)
            elapsed_time = datetime.datetime.now() - puser.get_last_reset_date()
            d = divmod(elapsed_time.total_seconds(), 60)
            # Divide the number of minutes by 60 minutes/hour * 24 hours/day => d / 1440
            # If at least 1 day (24 hours) has passed since the users last reset, reset their api calls and update db
            # Otherwise, redirect to error page
            if (d[0] / 1440) >= 1:
                puser.appCalls = 0
                puser.lastResetDate = datetime.datetime.now()
                puser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # Build list of user's cities saved in databaase
        for c in [puser.firstCity, puser.secondCity, puser.thirdCity]:
            if c is not None:
                cities.append(c)

        # Iterate over the user's cities, request forecast data from DarkSky API, then display them
        if cities is not None:
            for city in cities:
                location = geolocator.geocode(city)
                url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                    location.latitude) + ", " + str(location.longitude)
                darkskyjson = requests.get(url).json()
                weather = Parser.get_day_weather_basic(darkskyjson, city)
                weather_data_list.append(weather)
                apiCalls = apiCalls + 1

        # Update number of API calls made by user, save to database
        puser.appCalls = apiCalls
        puser.save()
        count = []
        context = {"weather_data_list": weather_data_list}
        return render(request, '..\\templates\premiumuser_daily_weather.html', context, count)
    else:
        # Get FreeUser object corresponding to username of logged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        # Get number of API calls made by user
        apiCalls = fuser.get_app_calls() if fuser.appCalls is not None else 0

        # See if the user has exceeded daily API calls
        if apiCalls > DAILY_API_CALLS_FREE_USERS:
            # Calculate the time between users last reset and now
            # d = (x minutes, y seconds)
            elapsed_time = datetime.datetime.now() - fuser.get_last_reset_date()
            d = divmod(elapsed_time.total_seconds(), 60)
            # Divide the number of minutes by 60 minutes/hour * 24 hours/day => d / 1440
            # If at least 1 day (24 hours) has passed since the users last reset, reset their api calls and update db
            # Otherwise, redirect to error page
            if (d[0] / 1440) >= 1:
                fuser.appCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        weather_data = []
        daily_data = []

        if fuser.firstCity is not None:
            location = geolocator.geocode(fuser.firstCity)
            url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
                location.latitude) + ", " + str(location.longitude)
            darkskyjson = requests.get(url).json()
            # Parse DarkSky data, update number of api calls made
            weather_data = Parser.get_day_weather_basic(darkskyjson, fuser.firstCity)
            apiCalls = apiCalls + 1

        # Update number of api calls made by user, save free user data to database
        fuser.appCalls = apiCalls
        fuser.save()
        context = {"weather_data": weather_data}
        return render(request, '..\\templates\\freeuser_daily_weather.html', context)


# Returns the index.html template
# Need to remove commented out code -- was just for testing purposes
# Should update index.html to display login/sign up/FAQ links
def index(request):
    # Pass custom ssl context so geopy will accept requests
   # ctx = ssl.create_default_context(cafile=certifi.where())
    #geopy.geocoders.options.default_ssl_context = ctx

    # Geoencode city 'Tampa'
   # geolocator = Nominatim(user_agent="Weeble")
    #location = geolocator.geocode("Tampa")

    # Build and send DarkSky request -- Replace secret key 'e49ed24b0e86f5466d6dde252a31addd' with your DarkSky API key
   # url = 'https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(location.latitude) + ", " + str(location.longitude)
   # darkskyjson = requests.get(url).json()

   # weather = Parser.get_current_weather_basic(darkskyjson)
    weather = []
    context = {"weather": weather,
               "city": "Tampa"}

    #pp = pprint.PrettyPrinter(indent=4)

    #pp.pprint(city_weather)
    #print("\n")
    #print(Parser.get_current_weather_basic(city_weather))
    #print("\n")
    #print(Parser.get_day_weather_basic(city_weather))
    #print("\n")
    #print(Parser.get_week_weather_basic(city_weather))

    # Print weather data
    #print(city_weather)

    return render(request, '..\\templates\weeble\index.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Accounts active without confrimation until emails are sending
            # user.is_active = False
            user.save()

            user.profile.isPremium = True if form.cleaned_data.get('isPremium') else False
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