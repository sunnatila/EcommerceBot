from django.contrib import admin
from click_up.models import ClickTransaction
from paytechuz.integrations.django.models import PaymentTransaction
from shared.excel_export import ExcelExportMixin

try:
    admin.site.unregister(ClickTransaction)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(PaymentTransaction)
except admin.sites.NotRegistered:
    pass

_CLICK_STATE_MAP = {
    'Yaratildi': 0,
    'Jarayonda': 1,
    'Muvaffaqiyatli': 2,
    'Bekor qilindi': -2,
}

_PAYME_STATE_MAP = {
    'Created': 0,
    'Initiating': 1,
    'Successfully': 2,
    'Cancelled after successful performed': -2,
    'Cancelled during initiation': -1,
}


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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Tranzaksiya ID, Order ID, Miqdor, Holat, Yaratilgan, Yangilangan
        id_ = int(row[0]) if row[0] else None
        state = _CLICK_STATE_MAP.get(str(row[4] or ''), 0)
        defaults = {
            'transaction_id': str(row[1] or ''),
            'account_id': int(row[2]) if row[2] else 0,
            'amount': row[3] or 0,
            'state': state,
        }
        if id_:
            ClickTransaction.objects.update_or_create(id=id_, defaults=defaults)
        else:
            ClickTransaction.objects.create(**defaults)


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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, gateway, Tranzaksiya ID, Order ID, Miqdor, Holat, Yaratilgan, Bajarilgan, Bekor qilingan
        id_ = int(row[0]) if row[0] else None
        state = _PAYME_STATE_MAP.get(str(row[5] or ''), 0)
        defaults = {
            'gateway': str(row[1] or 'payme'),
            'transaction_id': str(row[2] or ''),
            'account_id': str(row[3] or ''),
            'amount': row[4] or 0,
            'state': state,
        }
        if id_:
            PaymentTransaction.objects.update_or_create(id=id_, defaults=defaults)
        else:
            PaymentTransaction.objects.create(**defaults)
