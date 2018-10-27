from django.db import models

# Models for the three different database tables: Users, free users, and premium users.
# Free user/premium user models are linked to users via the userId field. Still need to
# get linking working properly with ForeignKey attribute


class User(models.Model):

    class Meta:
        db_table = 'users'

    FREE_USER = 'F'
    PREMIUM_USER = 'P'
    USER_TYPES = (
        (FREE_USER, 'Free User'),
        (PREMIUM_USER, 'Premium User')
    )

    userId = models.AutoField(null=False, unique=True, primary_key=True, db_column='UserID')
    userType = models.CharField(null=False, max_length=1, choices=USER_TYPES, default=FREE_USER, db_column='UserType')
    userName = models.CharField(null=False, blank=False, unique=True, max_length=30, db_column='UserName')
    password = models.CharField(null=False, blank=False, max_length=256, db_column='Password')
    email = models.EmailField(null=False, blank=False, unique=True, max_length=128, db_column='Email')
    registrationDate = models.DateField(null=False, auto_now=False, auto_now_add=True, db_column='RegistrationDate')
    lastLoginDate = models.DateField(null=True, auto_now=False, auto_now_add=False, db_column='LastLoginDate')

    def is_premium_user(self):
        return self.userType == self.PREMIUM_USER

    def is_free_user(self):
        return self.userType == self.FREE_USER

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

#    def __str__(self):
#        return "%s" % (self.userName)


class FreeUser(models.Model):

    class Meta:
        db_table='freeusers'

    userId = models.IntegerField(null=False, unique=True, db_column='UserID')
    freeUserId = models.AutoField(null=False, unique=True, primary_key=True, db_column='FreeUserID')
    firstCity = models.CharField(null=True, max_length=30, db_column='FirstCity')
    appCalls = models.IntegerField(null=False, default=0, db_column='APICalls')
    lastResetDate = models.DateTimeField(null=False, auto_now=False, auto_now_add=True, db_column='LastResetDate')
    # Having issues linking with ForeignKey; tests give errors when initializing/saving objects
#    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_user_id(self):
        return self.userId

    def get_free_user_id(self):
        return self.freeUserId

    def get_first_city(self):
        return self.firstCity

    def get_app_calls(self):
        return self.appCalls

    def get_last_reset_date(self):
        return self.lastResetDate

#    def __str__(self):
#       return "Free User: %s" % (self.userId)


class PremiumUser(models.Model):

    class Meta:
        db_table = 'premiumusers'

    userId = models.IntegerField(null=False, unique=True, db_column='UserID')
    premiumUserId = models.AutoField(null=False, unique=True, primary_key=True, db_column='PremiumUserID')
    firstCity = models.CharField(null=True, max_length=30, db_column='FirstCity')
    secondCity = models.CharField(null=True, max_length=30, db_column='SecondCity')
    thirdCity = models.CharField(null=True, max_length=30, db_column='ThirdCity')
    appCalls = models.IntegerField(null=False, default=0, db_column='APICalls')
    lastResetDate = models.DateTimeField(null=False, auto_now=False, auto_now_add=True, db_column='LastResetDate')
#    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_user_id(self):
        return self.userId

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

#    def get_user_name(self):
#        return self.user.userName

#    def __str__(self):
#        return "Premium User: %s" % (self.premiumUserId)



