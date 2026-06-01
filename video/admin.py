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

    excel_import_enabled = True

    def import_excel_row(self, row):
        # ID, Video URL, Tavsif
        id_ = int(row[0]) if row[0] else None
        defaults = {
            'video_url': str(row[1] or ''),
            'video_description': str(row[2] or ''),
        }
        if id_:
            Video.objects.update_or_create(id=id_, defaults=defaults)
        else:
            Video.objects.create(**defaults)
