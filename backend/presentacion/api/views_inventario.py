"""
Views para Inventario y Movimientos - SIMPLIFICADO con PDF y Email
Trabaja directamente con modelos sin casos de uso
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
    EmpresaModel,
)


class InventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Inventario - Con PDF y Email"""
    permission_classes = [IsAuthenticated]
    queryset = InventarioModel.objects.select_related('producto', 'empresa').all()
    
    def list(self, request, *args, **kwargs):
        """Listar todos los registros de inventario"""
        try:
            inventarios = InventarioModel.objects.select_related(
                'producto', 'empresa'
            ).all()
            
            # Serializar manualmente
            data = []
            for inv in inventarios:
                data.append({
                    'id': inv.id,
                    'producto': inv.producto.id,
                    'empresa': inv.empresa.id,
                    'stock_actual': inv.stock_actual,
                    'stock_minimo': inv.stock_minimo,
                    'stock_maximo': inv.stock_maximo,
                    'requiere_reorden': inv.requiere_reorden,
                    'producto_detalle': {
                        'id': inv.producto.id,
                        'codigo': inv.producto.codigo,
                        'nombre': inv.producto.nombre,
                        'precio_usd': float(inv.producto.precio_usd),
                    },
                    'empresa_detalle': {
                        'id': inv.empresa.id,
                        'nombre': inv.empresa.nombre,
                        'nit': inv.empresa.nit,
                    }
                })
            
            return Response(data)
        except Exception as e:
            print(f"Error en list inventario: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Ver detalle de un registro de inventario"""
        try:
            inv = InventarioModel.objects.select_related('producto', 'empresa').get(pk=pk)
            
            data = {
                'id': inv.id,
                'producto': inv.producto.id,
                'empresa': inv.empresa.id,
                'stock_actual': inv.stock_actual,
                'stock_minimo': inv.stock_minimo,
                'stock_maximo': inv.stock_maximo,
                'requiere_reorden': inv.requiere_reorden,
                'producto_detalle': {
                    'id': inv.producto.id,
                    'codigo': inv.producto.codigo,
                    'nombre': inv.producto.nombre,
                    'descripcion': inv.producto.descripcion,
                    'precio_usd': float(inv.producto.precio_usd),
                    'precio_cop': float(inv.producto.precio_cop) if inv.producto.precio_cop else 0,
                    'precio_eur': float(inv.producto.precio_eur) if inv.producto.precio_eur else 0,
                    'categoria': inv.producto.categoria,
                    'activo': inv.producto.activo,
                },
                'empresa_detalle': {
                    'id': inv.empresa.id,
                    'nombre': inv.empresa.nombre,
                    'nit': inv.empresa.nit,
                }
            }
            
            return Response(data)
        except InventarioModel.DoesNotExist:
            return Response({'error': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def productos_bajo_stock(self, request):
        """Obtener productos que requieren reorden"""
        try:
            inventarios = InventarioModel.objects.filter(
                requiere_reorden=True
            ).select_related('producto', 'empresa')
            
            data = []
            for inv in inventarios:
                data.append({
                    'id': inv.id,
                    'producto_detalle': {
                        'nombre': inv.producto.nombre,
                        'codigo': inv.producto.codigo,
                    },
                    'stock_actual': inv.stock_actual,
                    'stock_minimo': inv.stock_minimo,
                })
            
            return Response({
                'total': inventarios.count(),
                'productos': data
            })
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
            
            # Crear directorio media si no existe
            media_root = settings.MEDIA_ROOT
            os.makedirs(media_root, exist_ok=True)
            
            # Nombre del archivo
            fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f'inventario_{fecha}.pdf'
            ruta_archivo = os.path.join(media_root, nombre_archivo)
            
            # Crear PDF
            doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=1
            )
            
            elements.append(Paragraph('REPORTE DE INVENTARIO', title_style))
            elements.append(Paragraph(
                f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                styles['Normal']
            ))
            elements.append(Spacer(1, 0.5*inch))
            
            # Obtener inventarios
            inventarios = InventarioModel.objects.select_related('producto', 'empresa').all()
            
            # Crear tabla
            data = [['Código', 'Producto', 'Empresa', 'Stock', 'Mínimo', 'Precio USD', 'Estado']]
            
            for inv in inventarios:
                estado = '⚠️ REORDEN' if inv.requiere_reorden else '✓ OK'
                data.append([
                    inv.producto.codigo,
                    inv.producto.nombre[:30],
                    inv.empresa.nombre[:20],
                    str(inv.stock_actual),
                    str(inv.stock_minimo),
                    f'${inv.producto.precio_usd:.2f}' if hasattr(inv.producto, 'precio_usd') else 'N/A',
                    estado
                ])
            
            # Estilo de tabla
            table = Table(data, colWidths=[0.8*inch, 2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
            
            elements.append(table)
            
            # Estadísticas
            elements.append(Spacer(1, 0.5*inch))
            total_items = sum([inv.stock_actual for inv in inventarios])
            reorden_count = inventarios.filter(requiere_reorden=True).count()
            
            stats_style = ParagraphStyle(
                'Stats',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=10
            )
            
            elements.append(Paragraph(f'<b>Total de productos:</b> {inventarios.count()}', stats_style))
            elements.append(Paragraph(f'<b>Total de unidades:</b> {total_items}', stats_style))
            elements.append(Paragraph(f'<b>Productos que requieren reorden:</b> {reorden_count}', stats_style))
            
            # Generar PDF
            doc.build(elements)
            
            # Retornar URL
            url = f'{settings.MEDIA_URL}{nombre_archivo}'
            return Response({
                'mensaje': 'PDF generado exitosamente',
                'url': request.build_absolute_uri(url),
                'nombre_archivo': nombre_archivo
            })
            
        except Exception as e:
            print(f"Error al generar PDF: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def enviar_pdf_email(self, request):
        """Enviar PDF del inventario por email"""
        try:
            correo_destino = request.data.get('correo_destino')
            
            if not correo_destino:
                return Response(
                    {'error': 'El campo correo_destino es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generar PDF primero
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
            
            # Generar PDF
            doc = SimpleDocTemplate(ruta_archivo, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            elements.append(Paragraph('REPORTE DE INVENTARIO', styles['Heading1']))
            elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            inventarios = InventarioModel.objects.select_related('producto', 'empresa').all()
            
            data = [['Código', 'Producto', 'Empresa', 'Stock', 'Mínimo', 'Estado']]
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
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            doc.build(elements)
            
            # Enviar email
            email = EmailMessage(
                subject=f'Reporte de Inventario - {datetime.now().strftime("%d/%m/%Y")}',
                body=f'Adjunto encontrará el reporte de inventario generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}.\n\nTotal de productos: {inventarios.count()}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[correo_destino],
            )
            
            email.attach_file(ruta_archivo)
            email.send()
            
            return Response({
                'mensaje': f'PDF enviado exitosamente a {correo_destino}',
                'correo_destino': correo_destino
            })
            
        except Exception as e:
            print(f"Error al enviar email: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error al enviar email: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MovimientoViewSet(viewsets.ModelViewSet):
    """ViewSet para Movimientos de Inventario"""
    permission_classes = [IsAuthenticated]
    queryset = MovimientoInventarioModel.objects.select_related('producto', 'empresa').all()
    
    def list(self, request, *args, **kwargs):
        """Listar movimientos"""
        try:
            producto_id = request.query_params.get('producto_id')
            
            if producto_id:
                movimientos = MovimientoInventarioModel.objects.filter(
                    producto_id=producto_id
                ).select_related('producto', 'empresa').order_by('-fecha_movimiento')
            else:
                movimientos = MovimientoInventarioModel.objects.select_related(
                    'producto', 'empresa'
                ).order_by('-fecha_movimiento')[:100]
            
            data = []
            for mov in movimientos:
                data.append({
                    'id': mov.id,
                    'tipo_movimiento': mov.tipo_movimiento,
                    'cantidad': mov.cantidad,
                    'observaciones': mov.observaciones,
                    'fecha_movimiento': mov.fecha_movimiento,
                    'producto': mov.producto.id if mov.producto else None,
                    'empresa': mov.empresa.id if mov.empresa else None,
                })
            
            return Response(data)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def create(self, request, *args, **kwargs):
        """Crear movimiento de inventario"""
        try:
            producto_id = request.data.get('producto_id')
            tipo_movimiento = request.data.get('tipo_movimiento')
            cantidad = int(request.data.get('cantidad'))
            observaciones = request.data.get('observaciones', '')
            
            # Validar datos
            if not producto_id or not tipo_movimiento or not cantidad:
                return Response(
                    {'error': 'Faltan datos requeridos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener producto e inventario
            producto = ProductoModel.objects.get(id=producto_id)
            inventario = InventarioModel.objects.get(producto=producto)
            
            # Calcular nuevo stock según tipo de movimiento
            if tipo_movimiento == 'ENTRADA':
                inventario.stock_actual += cantidad
            elif tipo_movimiento == 'SALIDA':
                if inventario.stock_actual < cantidad:
                    return Response(
                        {'error': 'Stock insuficiente'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                inventario.stock_actual -= cantidad
            elif tipo_movimiento == 'AJUSTE':
                inventario.stock_actual = cantidad
            
            # Actualizar requiere_reorden
            inventario.requiere_reorden = inventario.stock_actual < inventario.stock_minimo
            inventario.save()
            
            # Crear movimiento
            movimiento = MovimientoInventarioModel.objects.create(
                tipo_movimiento=tipo_movimiento,
                producto=producto,
                cantidad=cantidad,
                empresa=inventario.empresa,
                usuario_id=request.user.id if request.user.is_authenticated else 1,
                observaciones=observaciones
            )
            
            return Response({
                'mensaje': 'Movimiento registrado exitosamente',
                'nuevo_stock': inventario.stock_actual
            }, status=status.HTTP_201_CREATED)
            
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except InventarioModel.DoesNotExist:
            return Response({'error': 'Inventario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
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
            
            elements.append(Paragraph('HISTORIAL DE MOVIMIENTOS', styles['Heading1']))
            elements.append(Paragraph(f'Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M")}', styles['Normal']))
            elements.append(Spacer(1, 0.3*inch))
            
            movimientos = MovimientoInventarioModel.objects.select_related(
                'producto', 'empresa'
            ).order_by('-fecha_movimiento')[:100]
            
            data = [['Fecha', 'Tipo', 'Producto', 'Cantidad', 'Observaciones']]
            for mov in movimientos:
                tipo_emoji = {
                    'ENTRADA': '📥',
                    'SALIDA': '📤',
                    'AJUSTE': '🔧'
                }.get(mov.tipo_movimiento, '')
                
                data.append([
                    mov.fecha_movimiento.strftime('%d/%m/%Y'),
                    f'{tipo_emoji} {mov.tipo_movimiento}',
                    mov.producto.nombre[:25] if mov.producto else 'N/A',
                    str(mov.cantidad),
                    (mov.observaciones[:30] + '...') if mov.observaciones and len(mov.observaciones) > 30 else (mov.observaciones or '-')
                ])
            
            table = Table(data, colWidths=[1*inch, 1.5*inch, 2.5*inch, 1*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
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
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {'error': f'Error al generar PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )