from django.db import models
from Kiepe.administrator.models import *
from django.contrib.auth import get_user_model
from geopy.geocoders import Nominatim
import string

# Create your models here.
class KibandaProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="kibanda", blank=True, null=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='kibanda_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coordinates = models.CharField(max_length=255, blank=True, null=True)  # user in ui he'll pick/pin the location from the map will be saved as coordinates
    aina_ya_ID = models.CharField(max_length=255, blank=True, null=True)
    ID_number = models.CharField(max_length=255, blank=True, null=True)
    usergroup = models.CharField(default="Kibanda", max_length=50)
    is_active = models.BooleanField(default=False)
    profile_is_completed = models.BooleanField(default=False)
    brand_name = models.CharField(max_length=255, blank=True, null=True)
    cover_photo = models.ImageField(upload_to="kibanda_images/", blank=True, null=True)
    is_default_meal_added = models.BooleanField(default=False)
    anadaiwa = models.BooleanField(default=False)
    physical_address = models.CharField(max_length=255, blank=True, null=True)
    profile_base64 = models.TextField(blank=True, null=True)
    cover_photo_base64 = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=255, default="FREE")
    # if user is free remember that we have his PaymentRecords with start and end date where the amount is 0..
    # so we'll use the PaymentRecords to check if kibanda Free tier expire or not..
    # free_startdate = models.DateTimeField(blank=True, null=True)  # we don't care about these two fields we're checking for PaymentRecords
    # free_enddate = models.DateTimeField(blank=True, null=True)  # we don't care about these two fields we're checking for PaymentRecords
    @property
    def name(self):
        return self.brand_name
    
    @property
    def category(self):
        return "Restaurant"

    @property
    def get_image(self):
        if self.image:
            return self.image.url
        return None

    @property
    def get_cover_photo(self):
        if self.cover_photo:
            return self.cover_photo.url
        return None

    @property
    def user_is_active(self):
        return self.user.is_active
    
    @property
    def phone_number(self):
        return self.user.phone_number

    @property
    def get_user_id(self):
        return self.user.id
    
    @property
    def is_kibanda_profile_active(self):
        return self.is_active
    
    @property
    def is_kibanda_opened(self):
        return self.kibandastatus.opened
    
    @property
    def capitalized_brand_name(self):
        return string.capwords(self.brand_name)

    @property
    def get_payments(self):
        payment = self.paymentrecord
        if payment:
            return {
                "id": payment.id,
                "amount": payment.amount,
                "start_date": payment.start_date,
                "expire_date": payment.expire_date
            }

        return None


    @property
    def average_ratings(self):
        ratings = self.kibandaratings.all()
        if ratings:
            total_ratings = 0
            for rating in ratings:
                total_ratings = total_ratings + rating.rating if rating.rating else total_ratings
            return total_ratings / ratings.count()
        return None

# hii itatupa taaarifa kama kwa siku hiyo kibanda kimefungwa or not.. kibanda kimoja kina status moja tu, hamna ku-create status nyingi 
# kiutimamu unachotakiwa kufanya ni ku-update tu status ya kibanda kama kimefungwa or kimefunguliwa... kiutimamu unavyo-create 
# user wa Kibanda also create the KibandaStatus instance for that kibanda, its the same to KibandaProfile...
# ko mtu anavyo-create Kibanda user also create KibandaProfile and KibandaStatus..
class KibandaStatus(models.Model):
    kibanda = models.OneToOneField(KibandaProfile, on_delete=models.CASCADE, related_name="kibandastatus")
    opened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



# hapa ndo ataweka price... initially unaweza uka-mu-allow kibanda acreate his menu items, the availableMenu should depend
# on this menu item so hapa kama kwenye livestreaming thabiti project mtu anavyo-create availableMenu of today 
# inabidi aweke MenuItem this menu item contains price of given menu by given Kibanda and so on if the dropdown 
# haina menuitem ambayo kibanda anataka a-add unaweza uka-mu-allow a-add new menu on popup window..
# 
class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    kibanda = models.ForeignKey(KibandaProfile, on_delete=models.CASCADE, related_name="menuitems")
    price = models.CharField(max_length=255, null=True, blank=True)  # we don't expect to have "price" for the "ingredietns" like tomato, pilipili, kachumbari
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # hii title ni muhimu kwa mfano mimi nauzi kuku but kuku - paja ni 5000, kuku - miguu ni 4000, kuku - kichwa ni 1000 etc.. 
    # but i don't know how it will look like in the ui

    @property
    def get_admin_menu(self):
        return {
            "id": self.menu.id,
            "name": self.menu.name,
        }

# menu ya leo ya kibanda fulani, vyakula vilivyopo kwa siku hiyo, hii ni onetoone coz inabid kila kibanda iwe na menu yake
# ya siku huska haman ku-create menu nyingje just update the menu for that day... hii itabidi awe anaijaza na anai-update kila
# wakati either chakula fulani kisipokuwepo and etc.. hii haina haja ya ku-create kila siku, coz kibanda kina menu yake ya kila siku
# hii menu hatucreate tunavyo-create kibanda user... hii ni onetoone haturuhusu kibanda kiwe na availableMenu nyingi itakuwa updated
# kila siku...
class AvailableMenu(models.Model):
    kibanda = models.OneToOneField(KibandaProfile, on_delete=models.CASCADE, related_name="menuyaleo")
    menu = models.ManyToManyField(MenuItem)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    set_from_default_menu = models.BooleanField(default=False)

    @property
    def get_kibanda(self):
        return {
            "id": self.kibanda.id,
        }
    
    @property
    def get_menu(self):
        menus = self.menu.all()
        menuItems = []
        if (menus.count() == 0):
            return None
        for menu in menus:
            menuItems.append({
                "id": menu.id,
                "menu": menu.menu.name,
                "price": menu.price,
                "parent_menu": menu.menu.id,
                "type": menu.menu.type,
            })
        return menuItems


# default menu item this is mostly used, most appeared in most days, allow user to have "sync" button to sync this menu item... this menu
# is mostly the last day menu before today availble menu.. so for first time/day when user add availableMenu for that day, the default menu
# will be of this kind.. Allow kibanda when first creating the availableMenu to set the menu as default one or not.. if not then allow him
# just kumrahisishia.... OR HAVE THE OPTIONS TO CREATE THE DEFAULT MENU FOR KIBANDA ... THIS IS CREATED ANYTIME..
class DefaultMenu(models.Model):
    kibanda = models.OneToOneField(KibandaProfile, on_delete=models.CASCADE, related_name="defaultmenu")
    menu = models.ManyToManyField(MenuItem, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    @property
    def get_kibanda(self):
        return {
            "id": self.kibanda.id,
        }

    @property
    def get_menu_list(self):
        menu_list = []
        if self.menu.all().count() > 0:
            for item in self.menu.all():
                # "menu_name": item.menu.name,
                # "price": item.menu.price,
                # item.menuitem_set ndo ya kibanda aliyo-add
                # ina price name and other metadata
                # print("dir ", dir(item.menuitem_set))
                menu_list.append({
                    "menuItemId": item.id,
                    "menuItemName": item.menu.name,
                    "menuItemPrice": item.price,
                    "parent_menu": item.menu.id,
                    "type": item.menu.type,
                })

            return menu_list
        return None