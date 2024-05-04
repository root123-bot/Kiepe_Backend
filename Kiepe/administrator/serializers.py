from .models import *
from rest_framework.serializers import ModelSerializer

class MenuSerializer(ModelSerializer):
    class Meta:
        model = Menu
        fields = [
            'id',
            'name',
            'get_image',
            'singular_name',
            'type',
            'get_popularity_score'
        ]



