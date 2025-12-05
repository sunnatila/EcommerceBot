from django.db import models



class User(models.Model):
    fullname = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    tg_id = models.CharField(max_length=50)
    created_at = models.DateField(auto_now=True)


    def __str__(self):
        return f"{self.pk} - {self.fullname}"

    class Meta:
        db_table = 'users'

