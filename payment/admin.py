from django.contrib import admin
from click_up.models import ClickTransaction
from paytechuz.integrations.django.models import PaymentTransaction
from shared.excel_export import ExcelExportMixin

# Kutubxonalar o'zlarining admin'larini ro'yxatga oladi — biz ularni override qilamiz
try:
    admin.site.unregister(ClickTransaction)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(PaymentTransaction)
except admin.sites.NotRegistered:
    pass


@admin.register(ClickTransaction)
class ClickTransactionAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ('id', 'transaction_id', 'account_id', 'amount', 'state', 'created_at', 'updated_at')
    search_fields = ('transaction_id', 'account_id')
    list_filter = ('state', 'created_at')
    ordering = ('-created_at',)

    excel_filename = 'click_tranzaksiyalar'
    excel_headers = [
        ('ID', 'id'),
        ('Tranzaksiya ID', 'transaction_id'),
        ('Order ID', 'account_id'),
        ('Miqdor', 'amount'),
        ('Holat', lambda obj: {0: 'Yaratildi', 1: 'Jarayonda', 2: 'Muvaffaqiyatli', -2: 'Bekor qilindi'}.get(obj.state, str(obj.state))),
        ('Yaratilgan', 'created_at'),
        ('Yangilangan', 'updated_at'),
    ]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ('id', 'gateway', 'transaction_id', 'account_id', 'amount', 'state', 'created_at')
    list_filter = ('gateway', 'state', 'created_at')
    search_fields = ('transaction_id', 'account_id')
    ordering = ('-created_at',)

    excel_filename = 'payme_tranzaksiyalar'
    excel_headers = [
        ('ID', 'id'),
        ("To'lov tizimi", 'gateway'),
        ('Tranzaksiya ID', 'transaction_id'),
        ('Order ID', 'account_id'),
        ('Miqdor', 'amount'),
        ('Holat', lambda obj: obj.get_state_display()),
        ('Yaratilgan', 'created_at'),
        ('Bajarilgan', 'performed_at'),
        ('Bekor qilingan', 'cancelled_at'),
    ]
