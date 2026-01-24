from rest_framework import serializers
from product.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'count', 'resolution', 'payment_method', 'cost', 'is_paid']
