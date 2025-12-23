from django.contrib import admin
from .models import User, AdminUser


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'fullname', 'phone_number', 'tg_id']


@admin.register(AdminUser)
class AdminUser(admin.ModelAdmin):
    list_display = ['id', 'username']
