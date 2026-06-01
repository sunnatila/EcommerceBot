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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Sarlavha, Tavsif, Narx(1080p), Narx(4K), Holat, Pozitsiya, Sana
        id_ = int(row[0]) if row[0] else None
        defaults = {
            'title': str(row[1] or ''),
            'description': str(row[2] or ''),
            'price_1080p': row[3] or 0,
            'price_4k': row[4] or 0,
            'is_active': str(row[5] or 'not_active'),
            'position': int(row[6]) if row[6] else 0,
        }
        if id_:
            Product.objects.update_or_create(id=id_, defaults=defaults)
        else:
            Product.objects.create(**defaults)


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

    excel_import_enabled = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('product')

    def import_excel_row(self, row):
        # ID, Foydalanuvchi, Mahsulotlar, Soni, Ruxsat, To'lov usuli, Narx, To'langan, Sana
        from user.models import User as UserModel

        id_ = int(row[0]) if row[0] else None

        # Foydalanuvchini ID dan ajratib olish: "1 - Ism" → 1
        user = None
        user_str = str(row[1] or '')
        try:
            user_id = int(user_str.split(' - ')[0])
            user = UserModel.objects.filter(id=user_id).first()
        except (ValueError, IndexError):
            pass
        if not user:
            raise ValueError(f"Foydalanuvchi topilmadi: '{user_str}'")

        defaults = {
            'user': user,
            'count': int(row[3]) if row[3] else 1,
            'resolution': str(row[4] or '1080p'),
            'payment_method': str(row[5] or ''),
            'cost': row[6] or 0,
            'is_paid': str(row[7]) == 'Ha',
        }

        if id_:
            order, _ = Order.objects.update_or_create(id=id_, defaults=defaults)
        else:
            order = Order.objects.create(**defaults)

        # Mahsulotlarni sarlavha orqali tiklash
        product_titles_str = str(row[2] or '')
        if product_titles_str:
            titles = [t.strip() for t in product_titles_str.split(', ') if t.strip()]
            products = Product.objects.filter(title__in=titles)
            order.product.set(products)
