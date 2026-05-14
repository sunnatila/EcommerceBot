import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.http import HttpResponse
from django.urls import path, reverse


class ExcelExportMixin:
    change_list_template = 'admin/excel_change_list.html'
    excel_filename = 'export'
    excel_headers = []  # [(ustun_nomi, field_nomi_yoki_callable), ...]

    def get_urls(self):
        app = self.model._meta.app_label
        model = self.model._meta.model_name
        return [
            path(
                'export-excel/',
                self.admin_site.admin_view(self.export_to_excel),
                name=f'{app}_{model}_export_excel',
            ),
        ] + super().get_urls()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        app = self.model._meta.app_label
        model = self.model._meta.model_name
        extra_context['export_excel_url'] = reverse(f'admin:{app}_{model}_export_excel')
        return super().changelist_view(request, extra_context=extra_context)

    def export_to_excel(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = self.excel_filename[:31]

        header_font = Font(bold=True, color='FFFFFF', size=11)
        header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        center = Alignment(horizontal='center', vertical='center')
        left = Alignment(horizontal='left', vertical='center')
        thin = Side(style='thin', color='BBBBBB')
        border = Border(left=thin, right=thin, top=thin, bottom=thin)

        for col, (label, _) in enumerate(self.excel_headers, 1):
            cell = ws.cell(row=1, column=col, value=label)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center
            cell.border = border

        queryset = self.get_queryset(request)
        for row, obj in enumerate(queryset, 2):
            for col, (_, field) in enumerate(self.excel_headers, 1):
                if callable(field):
                    value = field(obj)
                else:
                    raw = getattr(obj, field, '')
                    value = raw() if callable(raw) else raw
                cell = ws.cell(row=row, column=col, value=str(value) if value is not None else '')
                cell.border = border
                cell.alignment = left

        for col in ws.columns:
            max_len = max((len(str(c.value or '')) for c in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{self.excel_filename}.xlsx"'
        wb.save(response)
        return response
