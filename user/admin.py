from django.contrib import admin
from .models import User, AdminUser, BotStartUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'fullname', 'phone_number', 'tg_id']


@admin.register(AdminUser)
class AdminUser(admin.ModelAdmin):
    list_display = ['id', 'username']


@admin.register(BotStartUser)
class BotStartUser(admin.ModelAdmin):
    list_display = ['id', 'tg_id', 'fullname', 'username', 'started_at']

