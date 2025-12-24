from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from decimal import Decimal
import random
import time
from .models import PrediccionPrecio, ConsultaChatbot, AnalisisInventario
from .serializers import (
    PrediccionPrecioSerializer,
    ConsultaChatbotSerializer,
    CrearConsultaChatbotSerializer,
    AnalisisInventarioSerializer
)
from productos.models import Producto
from inventario.models import RegistroInventario

class PrediccionPrecioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para predicciones de precios con IA"""
    
    queryset = PrediccionPrecio.objects.all()
    serializer_class = PrediccionPrecioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def predecir_precio(self, request):
        """Genera una predicción de precio para un producto usando IA"""
        producto_id = request.data.get('producto_id')
        
        if not producto_id:
            return Response({
                'error': 'Debe proporcionar el ID del producto'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return Response({
                'error': 'Producto no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Simulación de predicción con IA (en producción usar OpenAI o modelo ML real)
        precio_actual = float(producto.precio_usd)
        
        # Factores simulados que influyen en el precio
        factores = {
            'tendencia_mercado': random.choice(['alcista', 'bajista', 'neutral']),
            'demanda_estimada': random.choice(['alta', 'media', 'baja']),
            'estacionalidad': random.choice(['alta', 'media', 'baja']),
            'competencia': random.choice(['alta', 'media', 'baja']),
        }
        
        # Calcular variación basada en factores (simulado)
        variacion_base = random.uniform(-0.15, 0.20)  # -15% a +20%
        
        if factores['tendencia_mercado'] == 'alcista':
            variacion_base += 0.05
        elif factores['tendencia_mercado'] == 'bajista':
            variacion_base -= 0.05
        
        # Predicciones a 30, 60 y 90 días
        precio_30 = Decimal(precio_actual * (1 + variacion_base * 0.3))
        precio_60 = Decimal(precio_actual * (1 + variacion_base * 0.6))
        precio_90 = Decimal(precio_actual * (1 + variacion_base * 1.0))
        
        # Determinar tendencia
        if variacion_base > 0.05:
            tendencia = 'ALZA'
        elif variacion_base < -0.05:
            tendencia = 'BAJA'
        else:
            tendencia = 'ESTABLE'
        
        # Confianza de la predicción (simulada)
        confianza = Decimal(random.uniform(65, 95))
        
        # Crear predicción
        prediccion = PrediccionPrecio.objects.create(
            producto=producto,
            precio_actual=producto.precio_usd,
            precio_predicho_30_dias=precio_30.quantize(Decimal('0.01')),
            precio_predicho_60_dias=precio_60.quantize(Decimal('0.01')),
            precio_predicho_90_dias=precio_90.quantize(Decimal('0.01')),
            tendencia=tendencia,
            confianza_prediccion=confianza.quantize(Decimal('0.01')),
            factores_considerados=factores,
            modelo_utilizado='Simulación IA - Demo'
        )
        
        serializer = PrediccionPrecioSerializer(prediccion)
        
        return Response({
            'mensaje': 'Predicción generada exitosamente',
            'prediccion': serializer.data,
            'recomendacion': self._generar_recomendacion(tendencia, confianza)
        })
    
    def _generar_recomendacion(self, tendencia, confianza):
        """Genera una recomendación basada en la tendencia"""
        if confianza < 70:
            base = "Confianza moderada en la predicción. "
        else:
            base = "Alta confianza en la predicción. "
        
        if tendencia == 'ALZA':
            return base + "Se recomienda mantener inventario y considerar aumentar precios gradualmente."
        elif tendencia == 'BAJA':
            return base + "Se recomienda reducir inventario y considerar promociones."
        else:
            return base + "Se recomienda mantener estrategia actual de precios."


class ChatbotViewSet(viewsets.ModelViewSet):
    """ViewSet para el chatbot de IA"""
    
    queryset = ConsultaChatbot.objects.all()
    serializer_class = ConsultaChatbotSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra consultas por usuario"""
        if self.request.user.tiene_permiso_administrador():
            return ConsultaChatbot.objects.all()
        return ConsultaChatbot.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['post'])
    def consultar(self, request):
        """Realiza una consulta al chatbot"""
        serializer = CrearConsultaChatbotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        pregunta = serializer.validated_data['pregunta']
        inicio = time.time()
        
        # Generar respuesta (simulada - en producción usar OpenAI GPT)
        respuesta, contexto = self._generar_respuesta(pregunta, request.user)
        
        tiempo_respuesta = Decimal(time.time() - inicio)
        
        # Guardar consulta
        consulta = ConsultaChatbot.objects.create(
            usuario=request.user,
            pregunta=pregunta,
            respuesta=respuesta,
            contexto=contexto,
            tiempo_respuesta=tiempo_respuesta.quantize(Decimal('0.01'))
        )
        
        return Response({
            'consulta_id': consulta.id,
            'pregunta': pregunta,
            'respuesta': respuesta,
            'tiempo_respuesta': float(tiempo_respuesta)
        })
    
    def _generar_respuesta(self, pregunta, usuario):
        """Genera una respuesta basada en la pregunta (simulado)"""
        pregunta_lower = pregunta.lower()
        
        # Respuestas simuladas basadas en palabras clave
        if 'producto' in pregunta_lower or 'inventario' in pregunta_lower:
            total_productos = Producto.objects.filter(activo=True).count()
            total_inventario = RegistroInventario.objects.count()
            
            respuesta = f"Actualmente hay {total_productos} productos activos en el sistema y {total_inventario} registros de inventario. "
            
            if 'bajo stock' in pregunta_lower or 'reorden' in pregunta_lower:
                bajo_stock = [r for r in RegistroInventario.objects.all() if r.requiere_reorden]
                respuesta += f"Hay {len(bajo_stock)} productos que requieren reorden."
            
            contexto = {
                'tipo_consulta': 'inventario',
                'total_productos': total_productos,
                'total_inventario': total_inventario
            }
        
        elif 'precio' in pregunta_lower:
            respuesta = "Puedo ayudarte con predicciones de precios. Usa la funcionalidad de predicción de precios para obtener análisis detallados basados en IA."
            contexto = {'tipo_consulta': 'precios'}
        
        elif 'empresa' in pregunta_lower:
            from empresas.models import Empresa
            total_empresas = Empresa.objects.filter(activo=True).count()
            respuesta = f"Hay {total_empresas} empresas activas en el sistema."
            contexto = {'tipo_consulta': 'empresas', 'total': total_empresas}
        
        else:
            respuesta = "Puedo ayudarte con información sobre inventario, productos, empresas y predicciones de precios. ¿Sobre qué te gustaría saber más?"
            contexto = {'tipo_consulta': 'general'}
        
        return respuesta, contexto


class AnalisisInventarioViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para análisis de inventario con IA"""
    
    queryset = AnalisisInventario.objects.all()
    serializer_class = AnalisisInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generar_analisis(self, request):
        """Genera un análisis completo del inventario"""
        
        # Obtener todos los registros de inventario
        registros = RegistroInventario.objects.filter(activo=True).select_related('producto', 'empresa')
        
        # Productos bajo stock
        bajo_stock = []
        sobrestock = []
        
        for registro in registros:
            if registro.requiere_reorden:
                bajo_stock.append({
                    'producto': registro.producto.nombre,
                    'codigo': registro.producto.codigo,
                    'cantidad_actual': registro.cantidad,
                    'cantidad_minima': registro.cantidad_minima,
                    'diferencia': registro.cantidad_minima - registro.cantidad
                })
            elif registro.cantidad > registro.cantidad_minima * 3:  # Más de 3x el mínimo
                sobrestock.append({
                    'producto': registro.producto.nombre,
                    'codigo': registro.producto.codigo,
                    'cantidad_actual': registro.cantidad,
                    'cantidad_minima': registro.cantidad_minima,
                    'exceso': registro.cantidad - (registro.cantidad_minima * 2)
                })
        
        # Recomendaciones
        recomendaciones = []
        
        if bajo_stock:
            recomendaciones.append({
                'tipo': 'urgente',
                'titulo': 'Productos bajo stock crítico',
                'descripcion': f'Se identificaron {len(bajo_stock)} productos que requieren reorden inmediato.',
                'accion': 'Generar orden de compra para productos críticos'
            })
        
        if sobrestock:
            costo_almacenamiento = sum(float(producto.precio_usd) * item['exceso'] 
                                       for item in sobrestock 
                                       for producto in Producto.objects.filter(codigo=item['codigo']))
            
            recomendaciones.append({
                'tipo': 'optimizacion',
                'titulo': 'Optimización de inventario',
                'descripcion': f'Se detectaron {len(sobrestock)} productos con exceso de stock.',
                'accion': f'Considerar promociones o reducir pedidos. Ahorro potencial: ${costo_almacenamiento:,.2f}'
            })
        
        # Proyección de demanda (simulada)
        proyeccion = {
            'proximos_30_dias': {
                'demanda_estimada': random.randint(100, 500),
                'productos_criticos': min(len(bajo_stock), 10)
            },
            'proximos_60_dias': {
                'demanda_estimada': random.randint(200, 800),
                'productos_criticos': min(len(bajo_stock), 15)
            }
        }
        
        # Calcular ahorro potencial
        ahorro_potencial = Decimal(sum(
            float(Producto.objects.get(codigo=item['codigo']).precio_usd) * item['exceso'] * 0.15
            for item in sobrestock
        ) if sobrestock else 0)
        
        # Crear análisis
        analisis = AnalisisInventario.objects.create(
            productos_analizados=registros.count(),
            recomendaciones=recomendaciones,
            productos_bajo_stock=bajo_stock,
            productos_sobrestock=sobrestock,
            proyeccion_demanda=proyeccion,
            ahorro_potencial=ahorro_potencial.quantize(Decimal('0.01'))
        )
        
        serializer = AnalisisInventarioSerializer(analisis)
        
        return Response({
            'mensaje': 'Análisis generado exitosamente',
            'analisis': serializer.data
        })