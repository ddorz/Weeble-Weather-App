from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Form for user sign up
class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    isPremium = forms.BooleanField(initial=False, required=False, label="Premium User",
                                      help_text='Select this option to sign up as a Premium User.')

    class Meta:
        model = User
        fields = ('username', 'isPremium', 'email', 'password1', )