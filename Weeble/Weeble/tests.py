from django.test import TestCase
from Weeble.models import User
from Weeble.models import FreeUser
from Weeble.models import PremiumUser
import datetime

# models test
class WeebleTest(TestCase):

    def create_user(self, userType, userName, password, email):
        return User.objects.create(userId=None, userType=userType, userName=userName, password=password,
                                     email=email, registrationDate=datetime.datetime.now(), lastLoginDate=None)

    def create_free_user(self, user):
        return FreeUser.objects.create(user=user, freeUserId=None, firstCity=None,
                                     appCalls=0, lastResetDate=datetime.datetime.now())

    def create_premium_user(self, user):
        return PremiumUser.objects.create(user=user, premiumUserId=None, firstCity=None, secondCity=None,
                                     thirdCity=None, appCalls=0, lastResetDate=datetime.datetime.now())

    def test_object_creation(self):
        # Create test user object
        testuser1 = self.create_user(User.FREE_USER, "FirstTestUser",
                                     "password", "testuser1@gmail.com")
        # Verify object creation
        self.assertTrue(isinstance(testuser1, User))

        # Create free user object
        freeusertest = self.create_free_user(testuser1)

        # Verify object creation
        self.assertTrue(isinstance(freeusertest, FreeUser))

        # Create second test user object
        testuser2 = self.create_user(User.PREMIUM_USER, "SecondTestUser",
                                     "password", "testuser2@gmail.com")

        # Verify object creation
        self.assertTrue(isinstance(testuser2, User))

        # Create premium user object
        premiumusertest = self.create_premium_user(testuser2)

        # Verify object creation
        self.assertTrue(isinstance(premiumusertest, PremiumUser))

    def test_object_saves(self):
        # Create test user
        testuser1 = User(None, User.FREE_USER, "FirstTestUser", "password",
                                       "testuser1@gmail.com", datetime.datetime.now(), None)
        # Save test user
        testuser1.save()
        # Verify user is free user
        self.assertTrue(testuser1.is_free_user())
        # Create free user using user info
        freeuser = FreeUser(testuser1, None, None, 0, datetime.datetime.now())
        # Save free user object
        freeuser.save()
        # Verify user and free user objects linked
        self.assertEqual(testuser1.get_user_name(), freeuser.get_user_name())

        # Create another test user
        testuser2 = User(None, User.PREMIUM_USER, "SecondTestUser", "password",
                                       "testuser2@gmail.com", datetime.datetime.now(), None)
        # Save test user
        testuser2.save()
        # Verify user is premium user
        self.assertTrue(testuser2.is_premium_user())
        # Create premium user object
        premiumuser = PremiumUser(testuser2, None, None, None, None, None, 0, datetime.datetime.now())
        # Save
        premiumuser.save()
        # Verify user and premium user objects are linked
        self.assertEqual(testuser2.get_user_name(), premiumuser.get_user_name())




