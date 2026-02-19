from django.core.exceptions import ValidationError
from django.db import models
from django.http.response import ResponseHeaders


class User(models.Model):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    tg_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateField(auto_now=True, null=True, blank=True)


    def __str__(self):
        return f"{self.pk} - {self.fullname}"

    class Meta:
        db_table = 'users'


class AdminUser(models.Model):
    username = models.CharField(max_length=255)


    objects = models.Manager()


    def __str__(self):
        return f"{self.pk} - {self.username}"

    def clean(self):
        if not self.pk and AdminUser.objects.exists():
            raise ValidationError("Admin allaqachon yaratilgan.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)



    class Meta:
        db_table = "admin_users"




class BotStartUser(models.Model):
    tg_id = models.CharField(max_length=50, null=True, blank=True)
    fullname = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    started_at = models.DateField(auto_now=True, null=True, blank=True)


    def __str__(self):
        return f"{self.pk} - {self.fullname}"



    class Meta:
        db_table = "bot_starts"
