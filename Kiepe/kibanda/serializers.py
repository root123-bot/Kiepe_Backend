from rest_framework.serializers import ModelSerializer
from .models import *

class KibandaProfileSerializer(ModelSerializer):
    class Meta:
        model = KibandaProfile
        fields = [
            'id',
            'first_name',
            'last_name',
            'get_image',
            'get_cover_photo',
            'coordinates',
            'created_at',
            'phone_number',
            'get_user_id',
            'profile_is_completed',
            'user_is_active',
            'is_kibanda_profile_active',
            'usergroup',
            'is_default_meal_added',
            'is_kibanda_opened',
            'brand_name',
            'physical_address',
            'capitalized_brand_name',
            'aina_ya_ID',
            'ID_number',
            'average_ratings',
            'get_payments',
            # 'cover_photo_base64',
            # 'profile_base64',
        ]

class KibandaSearchSuggestionSerializer(ModelSerializer):
    class Meta:
        model = KibandaProfile
        fields = [
            'id',
            'name',
            'category'
        ]

class KibandaDefaultMenuSerializer(ModelSerializer):
    class Meta:
        model = DefaultMenu
        fields = [
            'id',
            'get_kibanda',
            'get_menu_list',
        ]

class TodayAvailableMenuSerializer(ModelSerializer):
    class Meta:
        model = AvailableMenu
        fields = [
            'id',
            'get_kibanda',
            'get_menu',
            'set_from_default_menu'
        ]

class KibandaMapSerializer(ModelSerializer):
    class Meta: 
        model = KibandaProfile
        fields = [
            'id',
            'coordinates'
        ]


class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            'id',
            'price',
            'get_menu_id',
            'get_menu_name',
            'get_menu_type'
        ]

# this menus actually is "MenuItems" and can be fetched from KibandaProfile "menus" property
# so we need this in order to get price of given menu item of kibanda 
class SearchedMenuRestaurantSerializer(ModelSerializer):
    menus = MenuItemSerializer(many=True)

    class Meta:
        model = KibandaProfile
        fields = [
            'id',
            'get_image',
            'get_cover_photo',
            'coordinates',
            'get_user_id',
            'is_kibanda_profile_active',
            'is_kibanda_opened',
            'brand_name',
            'physical_address',
            'capitalized_brand_name',
            'average_ratings',
            'menus'
        ]
