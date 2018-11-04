from django.db import models
from django.contrib.auth.models import User

# Models for the three different database tables: Users, free users, and premium users.
# Free user/premium user models are linked to users via the username field. Still need to
# get linking working properly with ForeignKey attribute


class User(models.Model):

    class Meta:
        db_table = 'users'

    userId = models.AutoField(null=False, unique=True, primary_key=True, db_column='UserID')
    userName = models.CharField(null=False, blank=False, unique=True, max_length=30, db_column='UserName')
    password = models.CharField(null=False, blank=False, max_length=256, db_column='Password')
    email = models.CharField(null=False, blank=False, unique=True, max_length=128, db_column='Email')
    registrationDate = models.DateField(null=False, auto_now=False, auto_now_add=True, db_column='RegistrationDate')
    lastLoginDate = models.DateField(null=True, auto_now=False, auto_now_add=False, db_column='LastLoginDate')
    isPremium = models.BooleanField(null=False, db_column='isPremium')

    def is_premium_user(self):
        return self.isPremium

    def is_free_user(self):
        return self.isPremium == False

    def get_user_id(self):
        return self.userId

    def get_user_type(self):
        return self.userType

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


class FreeUser(models.Model):

    class Meta:
        db_table='freeusers'

    # FreeUser table changed to save username instead of user id. User/FreeUser tables now related by username
    #userId = models.IntegerField(null=False, unique=True, db_column='UserID')
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

    # PremiumUser table changed to save username instead of user id. User/PremiumUser tables now related by username
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