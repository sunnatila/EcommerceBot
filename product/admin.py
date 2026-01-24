from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price_1080p', 'price_4k', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'resolution', 'payment_method', 'cost', 'is_paid', 'created_at']
    list_filter = ['payment_method', 'is_paid', 'resolution']
    search_fields = ['id', 'user_id']