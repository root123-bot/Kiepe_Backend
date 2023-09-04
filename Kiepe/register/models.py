from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin, 
)
from django.core.validators import RegexValidator

# how to have email/phone as username and password as password https://stackoverflow.com/questions/72456647/django-login-with-email-or-phone-number

class UserManager(BaseUserManager):
    def _create_user(self, email, phone_number, password, **kwargs):
        email = self.normalize_email(email="notset@gmail.com")  
        phone_number = phone_number
        is_staff = kwargs.pop('is_staff', False)
        is_superuser = kwargs.pop('is_superuser', False)
        user = self.model(email=email, phone_number=phone_number, is_active=True, is_staff=is_staff, is_superuser=is_superuser, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_user(self, email, phone_number,  password=None, **extra_fields):
        return self._create_user(email, phone_number, password, **extra_fields)

    def create_superuser(self, email, phone_number, password, **extra_fields):
        return self._create_user(email, phone_number, password, is_staff=True, is_superuser=True, **extra_fields)  
       


phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")


# hii ndo model ambayo itatumika kum-authenticate user kwa kutumia email au phone number...
# hata uki-login kwa admin hiihii ndo inayotumika.. ko hapa tunaweka kuwa mtu either atumie
# email au phone number kama username na password kama password, 
# ko embu jiulize in our custom user model we defined the USERNAME_FIELD to be phone_number what about email?
# ok that is the default username field, but we can still use email as username, how?
# by using this backend, it will check if the username is a phone number or email, if it is a phone number
# it will check if the password is correct, if it is not it will check if the email is correct, if it is not it will return None
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # for now the email it can be duplicated since we set it to 'notset@gmail' for all devices regiseted in the system
    # we only need the phone number to be unique
    email = models.EmailField('email address', max_length=254, unique=False)
    phone_number = models.CharField(max_length=16, validators=[phone_validator], unique=True)
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_superuser = models.BooleanField('admin status', default=False)
    joined = models.DateTimeField('Date joined', auto_now_add=True)

    USERNAME_FIELD = 'phone_number'
    # REQUIRED_FIELD should be REQUIRED_FIELDS (plural), otherwise you won't be prompted for a username (or any other required fields) because Django did not find anything in REQUIRED_FIELDS
    # https://stackoverflow.com/questions/41612654/createsuperuser-didnt-ask-for-username
    # also the username field should not be in REQUIRED_FIELDS since by default it is required,
    # REQUIRED_FIELDS = ['email']
    def __str__(self):
        return self.email

    
    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email



    objects = UserManager()


# if the device phone, is not appear here then user put the phone number then send otp then 
# allow the user to set the new otp, hey also you should all, then logic behind the OTP 
# is just a random number you can use random module to create 6 digits number then for given
# phone just first check if the phone have the otp then update the OTP of that phone number
# don't create a new one.. 
class UserOTP(models.Model):
    phone = models.CharField(max_length=255)
    otp = models.CharField(max_length=6)
    alreadyUsed = models.BooleanField(default=False)
    