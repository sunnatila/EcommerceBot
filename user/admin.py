from django.contrib import admin
from .models import User, AdminUser, BotStartUser
from shared.excel_export import ExcelExportMixin


@admin.register(User)
class UserAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'fullname', 'username', 'tg_id']

    excel_filename = 'foydalanuvchilar'
    excel_headers = [
        ('ID', 'id'),
        ('Ism-Familiya', 'fullname'),
        ('Username', 'username'),
        ('Telegram ID', 'tg_id'),
        ("Ro'yxatdan o'tgan sana", 'created_at'),
    ]


@admin.register(AdminUser)
class AdminUserAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'username']

    excel_filename = 'adminlar'
    excel_headers = [
        ('ID', 'id'),
        ('Username', 'username'),
    ]


@admin.register(BotStartUser)
class BotStartUserAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'tg_id', 'fullname', 'username', 'started_at']

    excel_filename = 'bot_boshlagan_foydalanuvchilar'
    excel_headers = [
        ('ID', 'id'),
        ('Telegram ID', 'tg_id'),
        ('Ism-Familiya', 'fullname'),
        ('Username', 'username'),
        ('Boshlagan sana', 'started_at'),
    ]
