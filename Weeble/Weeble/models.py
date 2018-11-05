from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime

# Models for the three different database tables: Users, free users, and premium users.
# Since the object for the django database auth_users (django.contrib.models.User) is named User,
# the object for our 'users' table has been renamed to Profile. Our users table is linked to the
# auth_user table via the OneToOneField user_id (user) -- see below.
# Free user/premium user models share the 'username' field with the users table.


class Profile(models.Model):

    class Meta:
        db_table = 'users'

    # Link table to django auth_users table
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE, db_column='user_id')
    userName = models.CharField(null=False, blank=False, unique=True, max_length=30, db_column='UserName')
    password = models.CharField(null=False, blank=False, max_length=256, db_column='Password')
    email = models.CharField(null=False, blank=False, unique=True, max_length=128, db_column='Email')
    registrationDate = models.DateField(null=False, auto_now=False, auto_now_add=True, db_column='RegistrationDate')
    lastLoginDate = models.DateField(null=True, auto_now=False, auto_now_add=False, db_column='LastLoginDate')
    isPremium = models.BooleanField(null=False, db_column='isPremium')
    emailConfirmed = models.BooleanField(null=False, default=False)

    def get_user_id(self):
        return self.user

    def is_premium_user(self):
        return self.isPremium

    def is_free_user(self):
        return self.isPremium

    def get_user_name(self):
        return self.userName

    def get_encrypted_password(self):
        return self.password

    def get_email(self):
        return self.email

    def get_registration_date(self):
        return self.registrationDate

    def get_last_login_date(self):
        return self.lastLoginDate


# When a new user registers, an entry is created in the django auth_user db table, and automatically linked to an
# a new entry in the users db table.
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, userName="", password="", email="",
                               registrationDate=datetime.date.today(), lastLoginDate=datetime.date.today(),
                               isPremium=False, emailConfirmed=False)
    instance.profile.save()


class FreeUser(models.Model):

    class Meta:
        db_table='freeusers'

    userName = models.CharField(null=False, blank=False, unique=True, max_length=30, db_column='UserName')
    freeUserId = models.AutoField(null=False, unique=True, primary_key=True, db_column='FreeUserID')
    firstCity = models.CharField(null=True, max_length=30, db_column='FirstCity')
    appCalls = models.IntegerField(null=False, default=0, db_column='APICalls')
    lastResetDate = models.DateTimeField(null=False, auto_now=False, auto_now_add=True, db_column='LastResetDate')

    def get_user_name(self):
        return self.userName

    def get_free_user_id(self):
        return self.freeUserId

    def get_first_city(self):
        return self.firstCity

    def get_app_calls(self):
        return self.appCalls

    def get_last_reset_date(self):
        return self.lastResetDate


class PremiumUser(models.Model):

    class Meta:
        db_table = 'premiumusers'

    userName = models.CharField(null=False, blank=False, unique=True, max_length=30, db_column='UserName')
    premiumUserId = models.AutoField(null=False, unique=True, primary_key=True, db_column='PremiumUserID')
    firstCity = models.CharField(null=True, max_length=30, db_column='FirstCity')
    secondCity = models.CharField(null=True, max_length=30, db_column='SecondCity')
    thirdCity = models.CharField(null=True, max_length=30, db_column='ThirdCity')
    appCalls = models.IntegerField(null=False, default=0, db_column='APICalls')
    lastResetDate = models.DateTimeField(null=False, auto_now=False, auto_now_add=True, db_column='LastResetDate')

    def get_user_name(self):
        return self.userName

    def get_premium_user_id(self):
        return self.premiumUserId

    def get_first_city(self):
        return self.firstCity

    def get_second_city(self):
        return self.secondCity

    def get_third_city(self):
        return self.thirdCity

    def get_app_calls(self):
        return self.appCalls

    def get_last_reset_date(self):
        return self.lastResetDate