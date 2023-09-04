from rest_framework.serializers import ModelSerializer
from .models import *


class CustomerProfileSerializer(ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = [
            'id',
            'name',
            'is_active',
            'created_at',
            'phone_number',
            'get_image',
            'get_user_id',
            'usergroup',
        ]