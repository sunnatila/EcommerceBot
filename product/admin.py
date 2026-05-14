from django.contrib import admin
from .models import Product, Order
from shared.excel_export import ExcelExportMixin


@admin.register(Product)
class ProductAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'title', 'price_1080p', 'price_4k', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']

    excel_filename = 'mahsulotlar'
    excel_headers = [
        ('ID', 'id'),
        ('Sarlavha', 'title'),
        ('Tavsif', 'description'),
        ('Narx (1080p)', 'price_1080p'),
        ('Narx (4K)', 'price_4k'),
        ('Holat', 'is_active'),
        ('Pozitsiya', 'position'),
        ('Yaratilgan sana', 'created_at'),
    ]


@admin.register(Order)
class OrderAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'user_id', 'resolution', 'payment_method', 'cost', 'is_paid', 'created_at']
    list_filter = ['payment_method', 'is_paid', 'resolution']
    search_fields = ['id', 'user_id']

    excel_filename = 'buyurtmalar'
    excel_headers = [
        ('ID', 'id'),
        ('Foydalanuvchi', lambda obj: str(obj.user) if obj.user_id else ''),
        ('Mahsulotlar', lambda obj: ', '.join(p.title for p in obj.product.all())),
        ('Soni', 'count'),
        ('Ruxsat', 'resolution'),
        ("To'lov usuli", 'payment_method'),
        ('Narx', 'cost'),
        ("To'langan", lambda obj: 'Ha' if obj.is_paid else "Yo'q"),
        ('Sana', 'created_at'),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('product')
