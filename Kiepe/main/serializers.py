from rest_framework.serializers import ModelSerializer
from .models import *

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'order_id',
            'order_status',
            'order_date',
            'order_updated',
            'total',
            'get_assigned_to',
            'get_ordered_by',
            'get_order_items',
            'mark_as_deleted',
            'is_order_cancelled',
            'kibanda_mark_order_deleted',
        ]

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'get_menu',
            'quantity',
            'subtotal',
            'get_order_id',
        ]

class NotificationSerializer(ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'target',
            'heading',
            'body',
            'created_at',
            'is_read',
            'is_deleted',
            'get_order',
            'get_sent_to',
            'is_associted_with_order',
        ]

class KibandaRatingSerializer(ModelSerializer):
    class Meta:
        model = KibandaRating
        fields = [
            'id',
            'rating',
            'rating_comment',
            'rated_at',
        ]

class KibandaPaymentSerializer(ModelSerializer):
    class Meta:
        model = KibandaPayments
        fields = [
            "id",
            "payed_at",
            "amount",
            "get_kibanda",
            "start_date",
            "expire_date",
            
        ]