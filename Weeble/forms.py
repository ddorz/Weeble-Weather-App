from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from Weeble.models import FreeUser
from Weeble.models import PremiumUser
from django.forms import ModelForm, TextInput, NumberInput

# Form for user sign up
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    isPremium = forms.BooleanField(initial=False, required=False, label="Premium User",
                                      help_text='Select this option to sign up as a Premium User.')

    class Meta:
        model = User
        fields = ('username', 'isPremium', 'email', 'password1', )

# Form for free user home page
class CityFormFreeUser(forms.Form):
    city = forms.CharField(label='City Name', required=True, widget=TextInput(attrs={'class': 'input', 'placeholder': 'City Name'}))

# Form for premium user home page
class CityFormPremiumUser(forms.Form):
    city = forms.CharField(label='City Bus', widget=TextInput(attrs={'class': 'input', 'placeholder': 'City Name'}))
    city_number = forms.IntegerField(label='City Number', required=True, widget=TextInput(attrs={'class': 'input', 'placeholder': 'City Number'}))
