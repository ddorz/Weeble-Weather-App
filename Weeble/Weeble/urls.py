"""Weeble URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Path for index view -- This will be the home page for users not logged in
    path('', views.index),
    # Path for admin page
    path('admin/', admin.site.urls),
    # URL for home page -- home page for logged in users
    url(r'^home/$', views.home, name='home'),
    # URL for free users home page
    url(r'^homef/$', views.home, name='freeuser_home'),
    # URL for premium users home page
    url(r'^homep/$', views.home, name='premiumuser_home'),
    # URL for login page
    url(r'^login/$', auth_views.LoginView.as_view(template_name="..\\templates\login.html"), name="login"),
    # URL for page when users logout
    url(r'^logout/$',  auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    # URL for signup page
    url(r'^signup/$', views.signup, name='signup'),
    # Account activation email sent URL
    url(r'^account_activation_email_sent/$', views.account_activation_sent, name='account_activation_email_sent'),
    # Account activation / email confrimation URL
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    # URL for error page when user has no API calls left
    url(r'^APIerror/$', views.home, name='errorNoAPICalls'),
    # URL for error page when no new user accounts can be registered
    url(r'^registrationerror/$', views.home, name='registration_error'),
    # URL for free user weekly forecast page
    url(r'^fweeklyweather/$', views.weekly_weather, name='freeuser_weekly_weather'),
    # URL for free user daily forecast page
    url(r'^fdailyweather/$', views.daily_weather, name='freeuser_daily_weather'),
    # URL for premium user weekly forecast page
    url(r'^pweeklyweather/$', views.weekly_weather, name='premiumuser_weekly_weather'),
    # URL for premium user daily forecast page
    url(r'^pdailyweather/$', views.daily_weather, name='premiumuser_daily_weather'),
    #URL for faq
    path('faq/', views.faqView),
    # Path for loading city numbers for dropdown menu on premium user home page
    path('load_city_numbers/', views.load_city_numbers, name='load_city_numbers'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
