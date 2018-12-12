from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User
from Weeble.forms import CityFormFreeUser, CityFormPremiumUser
from Weeble.forms import SignUpForm
from Weeble.tokens import account_activation_token
from Weeble.models import Profile
from Weeble.models import FreeUser
from Weeble.models import PremiumUser
from Weeble.pbkdf2 import pbkdf2
import Weeble.darkskyparser as Parser
from geopy.geocoders import Nominatim
import datetime
import certifi
import ssl
import geopy.geocoders
import requests

DAILY_API_CALLS_FREE_USERS = 25
DAILY_API_CALLS_PREMIUM_USERS = 66
MAX_USERS = 20
MAX_FREE_USERS = 10
MAX_PREMIUM_USERS = 10


# Checks to see if a user's API calls can be reset, that is, if 1 day (24 hours) has passed since their last reset.
# Returns True if user's API calls can be reset, else False
def can_reset_user_api_calls(user_last_reset_date):
    elapsed_time = datetime.datetime.now() - user_last_reset_date  # Calculate time between last reset and now
    d = divmod(elapsed_time.total_seconds(), 60)                   # d = (x minutes, y seconds)
    return True if (d[0] / 1440) >= 1 else False                   # 60 minutes * 24 hours => 1440 minutes = 1 day


# Initialize geolocator object for encoding city names to coordinates
# Since the DarkSky API only accepts coordinates for weather data requests this allows users to search by city
# Returns geolocator object for geo-encoding cities to coordinates
def init_geolocator():
    # Pass custom ssl context so geopy will accept requests
    ctx = ssl.create_default_context(cafile=certifi.where())
    geopy.geocoders.options.default_ssl_context = ctx
    return Nominatim(user_agent="Weeble")


# Request forecast data from the DarkSky API via city name, Accepts geolocator object created by init_geolocator() and
# a city name, then encodes the city name to coordinates and makes the forecast data request to DarkSky API.
# Returns json object containing forecast data provided by DarkSky
def darksky_request_by_city(geolocator, city):
    location = geolocator.geocode(city)
    return requests.get('https://api.darksky.net/forecast/e49ed24b0e86f5466d6dde252a31addd/' + str(
        location.latitude) + ", " + str(location.longitude)).json()


# Generate city numbers for premium user home page
def load_city_numbers(request):
    city_numbers = []
    for i in range(0, PremiumUser.MAX_NUMBER_OF_CITIES):
        city_numbers.append(i + 1)
    return render(request, '..\\templates\city_number_dropdown_list.html', {'city_numbers': city_numbers})


@login_required(login_url='/login')
def home(request):
    # Initialize geolocator for encoding cities to coordinates
    geolocator = init_geolocator()

    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        puser = PremiumUser.objects.get(userName=profile.userName)
        api_calls = 0 if puser.apiCalls is None else puser.apiCalls
        cities = puser.get_saved_cities()
        weather_data = []

        # Verify the user has not used all their api calls -- we must modifiy DAILY_API_CALLS_PREMIUM_USER based on
        # the number of cities the premium user has saved, since each city will require an API call. If the user has
        # 1 API call left but 3 cities they we exceed their limit; so we subtract the number of saved cities + 1
        if api_calls >= DAILY_API_CALLS_PREMIUM_USERS-puser.get_number_of_saved_cities()+1:
            if can_reset_user_api_calls(puser.get_last_reset_date()):
                api_calls = puser.apiCalls = 0
                puser.lastResetDate = datetime.datetime.now()
                puser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # This will test true when data has been submitted via form (e.g. user selects 'Add City' button.
        # Here we get the data from the form (city and city number) and update our cities list.
        # The new city is updated in the database later before rendering the page (puser.save())
        if request.method == 'POST':
            form = CityFormPremiumUser(request.POST)
            if form.is_valid():
                city = form.cleaned_data.get('city')
                city_number = form.cleaned_data.get('city_number')
                valid_city_number = False
                for i in range(0, puser.MAX_NUMBER_OF_CITIES):
                    if city_number == i + 1:
                        valid_city_number = True
                        if len(cities) < city_number:
                            cities.append(city)
                        else:
                            cities[i] = city
                if valid_city_number:
                    puser.set_saved_cities(cities)

        form = CityFormPremiumUser()

        # Iterate over the user's cities, request forecast data from DarkSky API, then display data
        i = 1
        if cities is not None:
            for city in cities:
                darkskyjson = darksky_request_by_city(geolocator, city)
                weather = Parser.get_current_weather_basic(darkskyjson, city)
                weather["city_number"] = i
                weather_data.append(weather)
                api_calls = api_calls + 1
                i = i + 1

        # Save updated user object
        puser.apiCalls = api_calls
        puser.save()
        context = {"weather_data": weather_data, "form": form, "cities": cities}
        return render(request, '..\\templates\premiumuser_home.html', context)
    else:
        # Get FreeUser object corresponding to username of logged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        api_calls = 0 if fuser.apiCalls is None else fuser.apiCalls
        cities = [fuser.firstCity] if fuser.firstCity is not None else []
        weather_data = []

        # Verify the user has not used all their API calls
        if api_calls >= DAILY_API_CALLS_FREE_USERS:
            if can_reset_user_api_calls(fuser.get_last_reset_date()):
                api_calls = fuser.apiCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # True when user selects 'Add City' button
        if request.method == 'POST':
            form = CityFormFreeUser(request.POST)
            if form.is_valid():
                # Update the user's saved city
                fuser.firstCity = form.cleaned_data.get('city')
                # Request forecast data for city from DarkSky API
                darkskyjson = darksky_request_by_city(geolocator, fuser.get_first_city())
                # Parse DarkSky data, update number of api calls made
                weather = Parser.get_current_weather_basic(darkskyjson, fuser.get_first_city())
                weather_data.append(weather)
                api_calls = api_calls + 1
                cities = []

        form = CityFormFreeUser()

        if cities is not None:
            for city in cities:
                darkskyjson = darksky_request_by_city(geolocator, city)
                weather = Parser.get_current_weather_basic(darkskyjson, city)
                weather_data.append(weather)
                api_calls = api_calls + 1

        # Save updated user object to database
        fuser.apiCalls = api_calls
        fuser.save()
        context = {"weather_data": weather_data, "form": form, "cities": cities}
        return render(request, '..\\templates\\freeuser_home.html', context)


@login_required(login_url='/login')
def weekly_weather(request):
    # Initialize geopy
    geolocator = init_geolocator()
    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        COLUMN_FORMAT = {1: "column is-offset-6 is-6",
                         2: "column is-offset-4 is-4",
                         3: "column is-offset-2 is-8",
                         4: "column is-offset-2 is-8",
                         5: "column is-offset-1 is-10"}

        puser = PremiumUser.objects.get(userName=profile.userName)
        api_calls = 0 if puser.apiCalls is None else puser.apiCalls
        cities = puser.get_saved_cities()
        weather_data_list = []

        # See if the user has exceeded daily API calls
        if api_calls >= DAILY_API_CALLS_PREMIUM_USERS-puser.get_number_of_saved_cities()+1:
            if can_reset_user_api_calls(puser.get_last_reset_date()):
                api_calls = puser.apiCalls = 0
                puser.lastResetDate = datetime.datetime.now()
                puser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # Iterate over the user's cities, request forecast data from DarkSky API, then display them
        if cities is not None:
            for city in cities:
                darkskyjson = darksky_request_by_city(geolocator, city)
                weather = Parser.get_week_weather_basic(darkskyjson, city)
                weather_data_list.append(weather)
                api_calls = api_calls + 1

        # Save updated user object
        puser.apiCalls = api_calls
        puser.save()
        context = {"weather_data_list": weather_data_list, "column_format": COLUMN_FORMAT[len(cities)]}
        return render(request, '..\\templates\premiumuser_weekly_weather.html', context)
    else:
        # Get FreeUser object corresponding to username of lssogged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        api_calls = 0 if fuser.apiCalls is None else fuser.apiCalls
        weather_data = []

        # See if the user has exceeded daily API calls
        if api_calls >= DAILY_API_CALLS_FREE_USERS:
            if can_reset_user_api_calls(fuser.get_last_reset_date()):
                api_calls = fuser.apiCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        if fuser.firstCity is not None:
            darkskyjson = darksky_request_by_city(geolocator, fuser.get_first_city())
            weather_data = Parser.get_week_weather_basic(darkskyjson, fuser.get_first_city())
            api_calls = api_calls + 1

        # Save updated user object to database
        fuser.apiCalls = api_calls
        fuser.save()
        context = {"weather_data": weather_data}
        return render(request, '..\\templates\\freeuser_weekly_weather.html', context)


@login_required(login_url='/login')
def daily_weather(request):
    # Initialize geopy
    geolocator = init_geolocator()
    # Get user profile
    profile = Profile.objects.get(userName=request.user.username)

    # Redirect to either free user home page or premium user home paage depending on the on users account type
    if profile.isPremium:
        COLUMN_FORMAT = {1: "column is-offset-6 is-6",
                         2: "column is-offset-4 is-4",
                         3: "column is-offset-2 is-8",
                         4: "column is-offset-2 is-8",
                         5: "column is-offset-1 is-10"}
        puser = PremiumUser.objects.get(userName=profile.userName)
        api_calls = 0 if puser.apiCalls is None else puser.apiCalls
        cities = puser.get_saved_cities()
        weather_data_list = []

        # See if the user has exceeded daily API calls
        if api_calls >= DAILY_API_CALLS_PREMIUM_USERS-puser.get_number_of_saved_cities()+1:
            if can_reset_user_api_calls(puser.get_last_reset_date()):
                api_calls = puser.apiCalls = 0
                puser.lastResetDate = datetime.datetime.now()
                puser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        # Iterate over the user's cities, request forecast data from DarkSky API, then display them
        if cities is not None:
            for city in cities:
                darkskyjson = darksky_request_by_city(geolocator, city)
                weather = Parser.get_day_weather_basic(darkskyjson, city)
                weather_data_list.append(weather)
                api_calls = api_calls + 1

        # Save updated user object
        puser.apiCalls = api_calls
        puser.save()
        context = {"weather_data_list": weather_data_list, "column_format": COLUMN_FORMAT[len(cities)]}
        return render(request, '..\\templates\premiumuser_daily_weather.html', context)
    else:
        # Get FreeUser object corresponding to username of logged in user
        fuser = FreeUser.objects.get(userName=profile.userName)
        api_calls = 0 if fuser.apiCalls is None else fuser.apiCalls
        weather_data = []

        # See if the user has exceeded daily API calls
        if api_calls >= DAILY_API_CALLS_FREE_USERS:
            if can_reset_user_api_calls(fuser.get_last_reset_date()):
                api_calls = fuser.apiCalls = 0
                fuser.lastResetDate = datetime.datetime.now()
                fuser.save()
            else:
                return render(request, '..\\templates\errorNoAPICalls.html')

        if fuser.firstCity is not None:
            darkskyjson = darksky_request_by_city(geolocator, fuser.get_first_city())
            weather_data = Parser.get_day_weather_basic(darkskyjson, fuser.get_first_city())
            api_calls = api_calls + 1

        # Save updated user object to database
        fuser.apiCalls = api_calls
        fuser.save()
        context = {"weather_data": weather_data}
        return render(request, '..\\templates\\freeuser_daily_weather.html', context)


# TODO - Add home page -- currently redirects to login page
def index(request):
     return render(request, '..\\templates\weeble\\index.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Verify new users are being accepted. If at capacity and no new accounts can be registered, redirect user
            # to an error page. If there is room for new accounts but not of the type they selected, add error msg to
            # the form and display it on the page so user can sign up as different account type
            # TODO - Add input validation for email (verify valid email and verify not email not already registered)
            profile_list = Profile.objects.all()
            if len(profile_list) >= MAX_USERS:
                return render(request, '..\\templates\errorMaxAccounts.html')
            elif form.cleaned_data.get('isPremium') and len(PremiumUser.objects.all()) >= MAX_PREMIUM_USERS:
                form.add_error('isPremium', 'Sorry, we\'re currently not accepting new Premium Users')
                return render(request, '..\\templates\signup.html', {'form': form})
            elif not form.cleaned_data.get('isPremium') and len(FreeUser.objects.all()) >= MAX_FREE_USERS:
                form.add_error('isPremium', 'Sorry, we\'re currently not accepting new Free Users')
                return render(request, '..\\templates\signup.html', {'form': form})

            user = form.save(commit=False)
            user.is_active = False
            # Accounts active without confrimation until emails are sending
            # user.is_active = False
            user.save()

            user.profile.isPremium = True if form.cleaned_data.get('isPremium') else False
            user.profile.userName = form.cleaned_data.get('username')
            user.profile.password = pbkdf2(form.cleaned_data.get('password1'), 'salt')
            user.profile.email = form.cleaned_data.get('email')
            user.profile.registrationDate = datetime.datetime.today()
            # Accounts set to active without confirming email until we have a domain/STMP server to send emails
            user.profile.emailConfirmed = False
            user.profile.save()

            current_site = get_current_site(request)
            subject = 'Confirm your email to activate your Weeble Account'
            message = render_to_string('..\\templates\\account_activation.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })

            user.email_user(subject, message)
            username = form.cleaned_data.get('username')

            if form.cleaned_data.get('isPremium'):
                premiumuser = PremiumUser.objects.create(userName=username,
                                                         premiumUserId=None,
                                                         firstCity=None,
                                                         secondCity=None,
                                                         thirdCity=None,
                                                         fourthCity=None,
                                                         fifthCity=None,
                                                         apiCalls=0,
                                                         lastResetDate=datetime.datetime.now())
                premiumuser.save()
            else:
                freeuser = FreeUser.objects.create(userName=username,
                                                   freeUserId=None,
                                                   firstCity=None,
                                                   apiCalls=0,
                                                   lastResetDate=datetime.datetime.now())
                freeuser.save()

            return redirect('account_activation_email_sent')
    else:
        form = SignUpForm()
    return render(request, '..\\templates\signup.html', {'form': form})


def account_activation_sent(request):
    return render(request, '..\\templates\\account_activation_email_sent.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        # Get django.contrib.auth.User object. This is the django auth_user table
        user = User.objects.get(pk=uid)
        user.profile.emailConfirmed = False
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        # Set user object to active and save
        user.is_active = True
        user.is_superuser = False
        user.is_staff = False
        user.profile.emailConfirmed = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, '..\\templates\\account_activation_invalid_link.html')


def faqView(request):
    return render(request, '..\\templates\weeble\\faq.html')