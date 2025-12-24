from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
import os
from .models import RegistroInventario, MovimientoInventario
from .serializers import (
    RegistroInventarioSerializer,
    MovimientoInventarioSerializer,
    InventarioPorEmpresaSerializer
)
from empresas.views import EsAdministrador
from empresas.models import Empresa

class InventarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar inventario"""
    
    queryset = RegistroInventario.objects.all()
    serializer_class = RegistroInventarioSerializer
    permission_classes = [EsAdministrador]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'producto', 'activo']
    search_fields = ['producto__nombre', 'producto__codigo', 'ubicacion_bodega']
    ordering_fields = ['cantidad', 'valor_total', 'fecha_actualizacion']
    ordering = ['-fecha_actualizacion']
    
    def get_queryset(self):
        """Filtra el inventario según el usuario"""
        queryset = RegistroInventario.objects.select_related('producto', 'empresa')
        
        # Filtro de productos que requieren reorden
        requiere_reorden = self.request.query_params.get('requiere_reorden', None)
        if requiere_reorden == 'true':
            queryset = [reg for reg in queryset if reg.requiere_reorden]
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo registro de inventario"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'mensaje': 'Registro de inventario creado exitosamente',
            'registro': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def por_empresa(self, request):
        """Obtiene inventario agrupado por empresa"""
        empresa_nit = request.query_params.get('nit', None)
        
        if empresa_nit:
            try:
                empresa = Empresa.objects.get(nit=empresa_nit)
                registros = RegistroInventario.objects.filter(empresa=empresa)
                
                valor_total = sum(reg.valor_total for reg in registros)
                
                return Response({
                    'empresa': {
                        'nit': empresa.nit,
                        'nombre': empresa.nombre,
                    },
                    'registros': RegistroInventarioSerializer(registros, many=True).data,
                    'total_productos': registros.count(),
                    'valor_total': valor_total
                })
            except Empresa.DoesNotExist:
                return Response({
                    'error': 'Empresa no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Si no se especifica empresa, agrupar todos
        empresas = Empresa.objects.filter(activo=True)
        resultado = []
        
        for empresa in empresas:
            registros = RegistroInventario.objects.filter(empresa=empresa)
            if registros.exists():
                valor_total = sum(reg.valor_total for reg in registros)
                resultado.append({
                    'empresa': {
                        'nit': empresa.nit,
                        'nombre': empresa.nombre,
                    },
                    'total_productos': registros.count(),
                    'valor_total': float(valor_total)
                })
        
        return Response(resultado)
    
    @action(detail=False, methods=['get'])
    def productos_bajo_stock(self, request):
        """Obtiene productos que requieren reorden"""
        registros = RegistroInventario.objects.all()
        bajo_stock = [reg for reg in registros if reg.requiere_reorden]
        
        serializer = RegistroInventarioSerializer(bajo_stock, many=True)
        
        return Response({
            'total': len(bajo_stock),
            'registros': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def generar_pdf(self, request):
        """Genera un PDF con el inventario"""
        empresa_nit = request.data.get('empresa_nit', None)
        
        # Filtrar registros
        if empresa_nit:
            registros = RegistroInventario.objects.filter(
                empresa__nit=empresa_nit,
                activo=True
            ).select_related('producto', 'empresa')
            try:
                empresa = Empresa.objects.get(nit=empresa_nit)
                titulo = f"Inventario - {empresa.nombre}"
            except:
                return Response({
                    'error': 'Empresa no encontrada'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            registros = RegistroInventario.objects.filter(activo=True).select_related('producto', 'empresa')
            titulo = "Inventario General"
        
        # Crear PDF en memoria
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elementos = []
        
        # Estilos
        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=estilos['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        estilo_subtitulo = ParagraphStyle(
            'CustomSubtitle',
            parent=estilos['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#555555'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        # Título
        elementos.append(Paragraph(titulo, estilo_titulo))
        elementos.append(Paragraph(
            f"Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}",
            estilo_subtitulo
        ))
        elementos.append(Spacer(1, 0.3*inch))
        
        # Datos de la tabla
        datos_tabla = [['Código', 'Producto', 'Empresa', 'Cantidad', 'Ubicación', 'Precio USD', 'Valor Total']]
        
        valor_total_general = 0
        for reg in registros:
            datos_tabla.append([
                reg.producto.codigo,
                reg.producto.nombre[:30],  # Limitar longitud
                reg.empresa.nombre[:20],
                str(reg.cantidad),
                reg.ubicacion_bodega or '-',
                f"${reg.producto.precio_usd:,.2f}",
                f"${reg.valor_total:,.2f}"
            ])
            valor_total_general += reg.valor_total
        
        # Fila de total
        datos_tabla.append(['', '', '', '', '', 'TOTAL:', f"${valor_total_general:,.2f}"])
        
        # Crear tabla
        tabla = Table(datos_tabla, colWidths=[1*inch, 2*inch, 1.5*inch, 0.8*inch, 1*inch, 1*inch, 1*inch])
        
        # Estilo de la tabla
        tabla.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Cuerpo
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Cantidad centrada
            ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),  # Precios alineados a la derecha
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Fila de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a237e')),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1a237e')),
        ]))
        
        elementos.append(tabla)
        
        # Pie de página
        elementos.append(Spacer(1, 0.5*inch))
        elementos.append(Paragraph(
            f"Total de productos: {len(registros)} | Valor total del inventario: ${valor_total_general:,.2f} USD",
            estilos['Normal']
        ))
        
        # Generar PDF
        doc.build(elementos)
        buffer.seek(0)
        
        # Guardar temporalmente
        nombre_archivo = f"inventario_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'pdfs', nombre_archivo)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        
        with open(ruta_archivo, 'wb') as f:
            f.write(buffer.getvalue())
        
        # URL del archivo
        url_archivo = request.build_absolute_uri(settings.MEDIA_URL + 'pdfs/' + nombre_archivo)
        
        return Response({
            'mensaje': 'PDF generado exitosamente',
            'url': url_archivo,
            'nombre_archivo': nombre_archivo,
            'total_productos': len(registros),
            'valor_total': float(valor_total_general)
        })
    
    @action(detail=False, methods=['post'])
    def enviar_pdf_email(self, request):
        """Envía el PDF del inventario por email"""
        correo_destino = request.data.get('correo_destino')
        empresa_nit = request.data.get('empresa_nit', None)
        
        if not correo_destino:
            return Response({
                'error': 'Debe proporcionar un correo de destino'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar PDF
        pdf_response = self.generar_pdf(request)
        if pdf_response.status_code != 200:
            return pdf_response
        
        # Obtener nombre del archivo
        nombre_archivo = pdf_response.data['nombre_archivo']
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'pdfs', nombre_archivo)
        
        # Preparar email
        asunto = f"Inventario - {timezone.now().strftime('%d/%m/%Y')}"
        mensaje = f"""
        Estimado usuario,
        
        Adjunto encontrará el reporte de inventario solicitado.
        
        Detalles del reporte:
        - Total de productos: {pdf_response.data['total_productos']}
        - Valor total: ${pdf_response.data['valor_total']:,.2f} USD
        - Fecha de generación: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        
        Saludos cordiales,
        Sistema de Gestión de Inventario
        """
        
        try:
            email = EmailMessage(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [correo_destino]
            )
            
            # Adjuntar PDF
            with open(ruta_archivo, 'rb') as f:
                email.attach(nombre_archivo, f.read(), 'application/pdf')
            
            email.send()
            
            return Response({
                'mensaje': 'Email enviado exitosamente',
                'correo_destino': correo_destino,
                'nombre_archivo': nombre_archivo
            })
            
        except Exception as e:
            return Response({
                'error': f'Error al enviar email: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar movimientos de inventario"""
    
    queryset = MovimientoInventario.objects.all()
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_movimiento', 'registro_inventario']
    ordering = ['-fecha_movimiento']
    
    def perform_create(self, serializer):
        """Guarda el movimiento y actualiza el inventario"""
        movimiento = serializer.save(usuario=self.request.user)
        
        # Actualizar cantidad en inventario
        registro = movimiento.registro_inventario
        
        if movimiento.tipo_movimiento == 'ENTRADA':
            registro.cantidad += movimiento.cantidad
            registro.fecha_ultima_entrada = timezone.now()
        elif movimiento.tipo_movimiento == 'SALIDA':
            registro.cantidad -= movimiento.cantidad
            registro.fecha_ultima_salida = timezone.now()
        elif movimiento.tipo_movimiento == 'AJUSTE':
            # El ajuste establece la cantidad exacta
            registro.cantidad = movimiento.cantidad
        
        registro.save()