from django.db import models


class Video(models.Model):
    video_url = models.CharField(max_length=255)
    video_description = models.TextField()

    def __str__(self):
        return self.video_url

    class Meta:
        db_table = 'videos'
