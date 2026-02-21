"""
Mixins réutilisables pour views et models
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class BulkCreateModelMixin:
    """
    Mixin pour créer plusieurs objets en une seule requête
    POST /api/resource/bulk_create/
    {
        "objects": [
            {...},
            {...}
        ]
    }
    """
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        serializer = self.get_serializer(data=request.data.get('objects', []), many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'created': len(serializer.data),
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class ExportModelMixin:
    """
    Mixin pour exporter des données
    GET /api/resource/export/?format=csv
    GET /api/resource/export/?format=excel
    """
    @action(detail=False, methods=['get'])
    def export(self, request):
        format_type = request.query_params.get('format', 'csv')
        queryset = self.filter_queryset(self.get_queryset())
        
        if format_type == 'csv':
            return self._export_csv(queryset)
        elif format_type == 'excel':
            return self._export_excel(queryset)
        else:
            return Response(
                {'error': 'Format non supporté. Utilisez csv ou excel'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _export_csv(self, queryset):
        """Export CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        
        writer = csv.writer(response)
        
        # Headers
        if queryset.exists():
            fields = [field.name for field in queryset.model._meta.fields]
            writer.writerow(fields)
            
            # Data
            for obj in queryset:
                writer.writerow([getattr(obj, field) for field in fields])
        
        return response
    
    def _export_excel(self, queryset):
        """Export Excel"""
        from openpyxl import Workbook
        from django.http import HttpResponse
        
        wb = Workbook()
        ws = wb.active
        
        # Headers
        if queryset.exists():
            fields = [field.name for field in queryset.model._meta.fields]
            ws.append(fields)
            
            # Data
            for obj in queryset:
                ws.append([getattr(obj, field) for field in fields])
        
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="export.xlsx"'
        
        wb.save(response)
        return response