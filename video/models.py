from django.core.exceptions import ValidationError
from django.db import models




class Video(models.Model):
    video_url = models.CharField(max_length=255)
    video_description = models.TextField()

    def __str__(self):
        return self.video_url

    class Meta:
        db_table = 'videos'

    def clean(self):
        if not self.pk and Video.objects.exists():
            raise ValidationError("Admin allaqachon yaratilgan.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

