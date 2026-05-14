from django.contrib import admin
from .models import Video
from shared.excel_export import ExcelExportMixin


@admin.register(Video)
class VideoAdmin(ExcelExportMixin, admin.ModelAdmin):
    list_display = ['id', 'video_url']

    excel_filename = 'videolar'
    excel_headers = [
        ('ID', 'id'),
        ('Video URL', 'video_url'),
        ('Tavsif', 'video_description'),
    ]
