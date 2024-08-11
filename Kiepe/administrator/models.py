from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
'''
    Difference btn auto_now_add and auto_now
    From django docs: “”" auto_now Automatically set the field to now every time the object is saved. Useful for “last-modified” timestamps. Note that the current date is always used; it’s not just a default value that you can override.

    auto_now_add Automatically set the field to now when the object is first created. Useful for creation of timestamps. Note that the current date is always used; it’s not just a default value that you can override. “”"

    I think it is very simple task to implement auto_now
    this is the same to menuItem.... here we have "Chipsi", "Kuku", "Soseji" and so on
    which we'll be taken by "Kibanda" and get Added to the "AvailableMenu" of the day
    hii sjamaanisha ni full dish like "chipsi yai" hapana hii ni individual "menuIte" na 
    ndo ambayo inatumika kwa Kibanda ku-create "MenuItem" 
'''


class Menu(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    singular_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, default="menu")


    def __str__(self):
        return self.name

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        return None

    @property
    def get_popularity_score(self):
        # then lets count the number of times this menu appears in the menuitems, if it appears more then it's popular than the rest
        return self.menuitem_set.count() + self.orderitem_set.count()

    @property
    def category(self):
        return "Food"

class AdminProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    profile = models.ImageField(
        upload_to='admin_profile_images/', blank=True, null=True)


class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
