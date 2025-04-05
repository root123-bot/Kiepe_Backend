from django.contrib.auth.hashers import check_password
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

# hii ndo model ambayo itatumika kum-authenticate user kwa kutumia email au phone number...
# hata uki-login kwa admin hiihii ndo inayotumika.. ko hapa tunaweka kuwa mtu either atumie
# email au phone number kama username na password kama password, 
# ko embu jiulize in our custom user model we defined the USERNAME_FIELD to be phone_number what about email?
# ok that is the default username field, but we can still use email as username, how?
# by using this backend, it will check if the username is a phone number or email, if it is a phone number
# it will check if the password is correct, if it is not it will check if the email is correct, if it is not it will return None
class EmailPhoneUsernameAuthenticationBackend(object):
    @staticmethod
    def authenticate(request, username=None, password=None):
        print('this is what i receive ', username, password)
        try:
            user = User.objects.get(
                Q(phone_number=username) | Q(email=username)
            )

        except User.DoesNotExist:
            return None

        if user and check_password(password, user.password):
            return user

        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
