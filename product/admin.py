from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'is_active']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'payment_method', 'is_paid', 'created_at']
    list_filter = ['payment_method', 'is_paid']
    search_fields = ['id', 'user_id', 'product_id']

