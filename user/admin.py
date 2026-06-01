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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Ism-Familiya, Username, Telegram ID, Sana
        id_ = int(row[0]) if row[0] else None
        defaults = {
            'fullname': str(row[1]) if row[1] else None,
            'username': str(row[2]) if row[2] else None,
            'tg_id': str(row[3]) if row[3] else None,
        }
        if id_:
            User.objects.update_or_create(id=id_, defaults=defaults)
        else:
            User.objects.create(**defaults)


@admin.register(AdminUser)
class AdminUserAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'username']

    excel_filename = 'adminlar'
    excel_headers = [
        ('ID', 'id'),
        ('Username', 'username'),
    ]

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Username
        id_ = int(row[0]) if row[0] else None
        username = str(row[1] or '').strip()
        if not username:
            return
        # Mavjud yozuvni yangilash (full_clean ni chetlab o'tish uchun filter().update())
        if id_ and AdminUser.objects.filter(id=id_).exists():
            AdminUser.objects.filter(id=id_).update(username=username)
        elif not AdminUser.objects.exists():
            # bulk_create full_clean ni chaqirmaydi
            AdminUser.objects.bulk_create([AdminUser(id=id_, username=username)])


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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Telegram ID, Ism-Familiya, Username, Sana
        id_ = int(row[0]) if row[0] else None
        defaults = {
            'tg_id': str(row[1]) if row[1] else None,
            'fullname': str(row[2]) if row[2] else None,
            'username': str(row[3]) if row[3] else None,
        }
        if id_:
            BotStartUser.objects.update_or_create(id=id_, defaults=defaults)
        else:
            BotStartUser.objects.create(**defaults)
