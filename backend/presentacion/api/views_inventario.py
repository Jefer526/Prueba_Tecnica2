"""
Views para Inventario - CAMPOS CORRECTOS según modelo real
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.core.mail import EmailMessage
import os

from infraestructura.django_orm.models import (
    InventarioModel,
    MovimientoInventarioModel,
    ProductoModel,
)
from presentacion.api.serializers_inventario import (
    InventarioListaSerializer,
    InventarioDetalleSerializer,
    MovimientoInventarioListaSerializer,
    MovimientoInventarioCrearSerializer,
)


class InventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Inventario"""
    permission_classes = [IsAuthenticated]
    queryset = InventarioModel.objects.select_related('producto', 'empresa').all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return InventarioDetalleSerializer
        return InventarioListaSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar inventario"""
        try:
            inventarios = InventarioModel.objects.select_related('producto', 'empresa').all()
            serializer = InventarioListaSerializer(inventarios, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def productos_bajo_stock(self, request):
        """Productos que requieren reorden"""
        try:
            inventarios = InventarioModel.objects.filter(
                requiere_reorden=True
            ).select_related('producto', 'empresa')
            serializer = InventarioListaSerializer(inventarios, many=True)
            return Response({'total': inventarios.count(), 'productos': serializer.data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        """Generar PDF del inventario"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from datetime import datetime
            
            media_root = settings.MEDIA_ROOT
            os.makedirs(media_root, exist_ok=True)
            
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'inventario_{fecha}.pdf'
            ruta_archivo = os.path.join(media_root, nombre_archivo)
            
            doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=1
            )
            elements.append(Paragraph('REPORTE DE INVENTARIO', title_style))
            elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            inventarios = InventarioModel.objects.select_related('producto', 'empresa').all()
            
            data = [['Código', 'Producto', 'Empresa', 'Stock', 'Stock Mín.', 'Estado']]
            
            for inv in inventarios:
                estado = '⚠️ REORDEN' if inv.requiere_reorden else '✓ OK'
                data.append([
                    inv.producto.codigo,
                    inv.producto.nombre[:30],
                    inv.empresa.nombre[:20],
                    str(inv.stock_actual),
                    str(inv.stock_minimo),
                    estado
                ])
            
            table = Table(data, colWidths=[0.8*inch, 2.5*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
            total_productos = inventarios.count()
            total_items = sum([inv.stock_actual for inv in inventarios])
            productos_reorden = inventarios.filter(requiere_reorden=True).count()
            
            elements.append(Paragraph(f'<b>Total Productos:</b> {total_productos}', styles['Normal']))
            elements.append(Paragraph(f'<b>Total Items:</b> {total_items}', styles['Normal']))
            elements.append(Paragraph(f'<b>Requieren Reorden:</b> {productos_reorden}', styles['Normal']))
            
            doc.build(elements)
            
            url = f'{settings.MEDIA_URL}{nombre_archivo}'
            return Response({
                'mensaje': 'PDF generado exitosamente',
                'url': request.build_absolute_uri(url),
                'nombre_archivo': nombre_archivo
            })
        except Exception as e:
            print(f"Error PDF: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def enviar_pdf_email(self, request):
        """Enviar PDF por email"""
        try:
            correo_destino = request.data.get('correo_destino')
            if not correo_destino:
                return Response({'error': 'correo_destino es requerido'}, status=status.HTTP_400_BAD_REQUEST)
            
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from datetime import datetime
            
            media_root = settings.MEDIA_ROOT
            os.makedirs(media_root, exist_ok=True)
            
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'inventario_{fecha}.pdf'
            ruta_archivo = os.path.join(media_root, nombre_archivo)
            
            doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph('REPORTE DE INVENTARIO', styles['Heading1']))
            elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            inventarios = InventarioModel.objects.select_related('producto', 'empresa').all()
            
            data = [['Código', 'Producto', 'Empresa', 'Stock', 'Estado']]
            for inv in inventarios:
                estado = '⚠️' if inv.requiere_reorden else '✓'
                data.append([
                    inv.producto.codigo,
                    inv.producto.nombre[:30],
                    inv.empresa.nombre[:20],
                    str(inv.stock_actual),
                    estado
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            email = EmailMessage(
                subject=f'Reporte de Inventario - {datetime.now().strftime("%d/%m/%Y")}',
                body=f'Adjunto reporte de inventario.\n\nTotal productos: {inventarios.count()}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[correo_destino],
            )
            
            email.attach_file(ruta_archivo)
            email.send()
            
            return Response({'mensaje': f'PDF enviado a {correo_destino}', 'correo_destino': correo_destino})
        except Exception as e:
            print(f"Error email: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovimientoViewSet(viewsets.ModelViewSet):
    """ViewSet para Movimientos"""
    permission_classes = [IsAuthenticated]
    queryset = MovimientoInventarioModel.objects.select_related('producto', 'empresa').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return MovimientoInventarioCrearSerializer
        return MovimientoInventarioListaSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar movimientos"""
        try:
            movimientos = self.queryset.all().order_by('-fecha_movimiento')
            serializer = MovimientoInventarioListaSerializer(movimientos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Registrar movimiento"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            producto_id = serializer.validated_data['producto_id']
            tipo = serializer.validated_data['tipo_movimiento']
            cantidad = serializer.validated_data['cantidad']
            observaciones = serializer.validated_data.get('observaciones', '')
            
            # Obtener producto
            producto = ProductoModel.objects.get(id=producto_id)
            
            # Obtener o crear inventario
            inventario, created = InventarioModel.objects.get_or_create(
                producto=producto,
                defaults={
                    'empresa': producto.empresa,
                    'stock_actual': 0,
                    'stock_minimo': 10,
                }
            )
            
            # Actualizar stock
            if tipo == 'ENTRADA':
                inventario.stock_actual += cantidad
            elif tipo == 'SALIDA':
                if inventario.stock_actual < cantidad:
                    return Response(
                        {'error': 'Stock insuficiente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                inventario.stock_actual -= cantidad
            else:  # AJUSTE
                inventario.stock_actual = cantidad
            
            # Verificar reorden
            inventario.requiere_reorden = inventario.stock_actual <= inventario.stock_minimo
            inventario.save()
            
            # Crear movimiento
            movimiento = MovimientoInventarioModel.objects.create(
                tipo_movimiento=tipo,
                producto=producto,
                cantidad=cantidad,
                empresa=producto.empresa,
                usuario_id=request.user.id if request.user.is_authenticated else 1,
                observaciones=observaciones
            )
            
            response_serializer = MovimientoInventarioListaSerializer(movimiento)
            return Response(
                {'mensaje': 'Movimiento registrado exitosamente', 'movimiento': response_serializer.data},
                status=status.HTTP_201_CREATED
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error movimiento: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def generar_pdf(self, request):
        """Generar PDF de movimientos"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from datetime import datetime
            
            media_root = settings.MEDIA_ROOT
            os.makedirs(media_root, exist_ok=True)
            
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'movimientos_{fecha}.pdf'
            ruta_archivo = os.path.join(media_root, nombre_archivo)
            
            doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph('REPORTE DE MOVIMIENTOS', styles['Heading1']))
            elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            movimientos = MovimientoInventarioModel.objects.select_related('producto').order_by('-fecha_movimiento')[:100]
            
            data = [['Fecha', 'Producto', 'Tipo', 'Cantidad', 'Observaciones']]
            
            for mov in movimientos:
                data.append([
                    mov.fecha_movimiento.strftime('%d/%m/%Y %H:%M'),
                    mov.producto.nombre[:30],
                    mov.tipo_movimiento,
                    str(mov.cantidad),
                    mov.observaciones[:30] if mov.observaciones else 'N/A'
                ])
            
            table = Table(data, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            url = f'{settings.MEDIA_URL}{nombre_archivo}'
            return Response({
                'mensaje': 'PDF generado exitosamente',
                'url': request.build_absolute_uri(url),
                'nombre_archivo': nombre_archivo
            })
        except Exception as e:
            print(f"Error PDF: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)