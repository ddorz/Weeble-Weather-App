from datetime import date
from django.utils import six
from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class AccountActivationTokenGenerator:

    key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"
    secret = settings.SECRET_KEY

    def make_token(self, user):
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        if not (user and token):
            return False
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid has not been tampered with
        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        # Check the timestamp is within limit. Timestamps are rounded to
        # midnight (server time) providing a resolution of only 1 day. If a
        # link is generated 5 minutes before midnight and used 6 minutes later,
        # that counts as 1 day. Therefore, PASSWORD_RESET_TIMEOUT_DAYS = 1 means
        # "at least 1 day, could be up to 2."
        if (self._num_days(self._today()) - ts) > settings.PASSWORD_RESET_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        # timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
            secret=self.secret,
        ).hexdigest()[::2]  # Limit to 20 characters to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.username) + six.text_type(timestamp) +
            six.text_type(user.profile.emailConfirmed)
        )

    def _num_days(self, dt):
        return (dt - date(2001, 1, 1)).days

    def _today(self):
        # Used for mocking in tests
        return date.today()


account_activation_token = AccountActivationTokenGenerator()