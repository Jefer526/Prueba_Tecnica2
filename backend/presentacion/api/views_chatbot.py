"""
Vistas del Chatbot - Capa de Presentación
Coordinan HTTP y delegan lógica a los casos de uso
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from presentacion.api.serializers_chatbot import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ConversacionSerializer
)

# Importar casos de uso
from aplicacion.casos_uso.chatbot import (
    EnviarMensajeChatbotCasoDeUso,
    ConsultarStockCasoDeUso,
    ObtenerProductosBajoStockCasoDeUso,
    BuscarProductoCasoDeUso,
    ObtenerEstadisticasInventarioCasoDeUso
)

# Importar repositorios
from infraestructura.django_orm.repositorio_producto import RepositorioProductoDjango
from infraestructura.django_orm.repositorios import (
    RepositorioInventarioDjango,
    RepositorioMovimientoDjango
)

# Importar models de Django para conversaciones
from infraestructura.django_orm.models import (
    ConversacionModel,
    MensajeModel
)


class ChatbotView(APIView):
    """
    POST: Enviar mensaje al chatbot
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Enviar mensaje al chatbot usando casos de uso"""
        serializer = ChatRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mensaje_usuario = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        
        try:
            with transaction.atomic():
                # Obtener o crear conversación
                if conversacion_id:
                    try:
                        conversacion = ConversacionModel.objects.get(
                            id=conversacion_id,
                            usuario_id=request.user.id,
                            activo=True
                        )
                    except ConversacionModel.DoesNotExist:
                        conversacion = ConversacionModel.objects.create(
                            usuario_id=request.user.id,
                            titulo=mensaje_usuario[:50]
                        )
                else:
                    conversacion = ConversacionModel.objects.create(
                        usuario_id=request.user.id,
                        titulo=mensaje_usuario[:50]
                    )
                
                # Guardar mensaje del usuario
                mensaje_user = MensajeModel.objects.create(
                    conversacion=conversacion,
                    rol='user',
                    contenido=mensaje_usuario
                )
                
                # Instanciar repositorios
                repo_producto = RepositorioProductoDjango()
                repo_inventario = RepositorioInventarioDjango()
                repo_movimiento = RepositorioMovimientoDjango()
                
                # Instanciar casos de uso
                caso_uso_stock = ConsultarStockCasoDeUso(
                    repositorio_inventario=repo_inventario,
                    repositorio_producto=repo_producto
                )
                
                caso_uso_bajo_stock = ObtenerProductosBajoStockCasoDeUso(
                    repositorio_inventario=repo_inventario,
                    repositorio_producto=repo_producto  # ✅ Agregar repositorio
                )
                
                caso_uso_buscar = BuscarProductoCasoDeUso(
                    repositorio_producto=repo_producto,
                    repositorio_inventario=repo_inventario
                )
                
                caso_uso_estadisticas = ObtenerEstadisticasInventarioCasoDeUso(
                    repositorio_inventario=repo_inventario,
                    repositorio_movimiento=repo_movimiento
                )
                
                # Caso de uso principal
                caso_uso_chatbot = EnviarMensajeChatbotCasoDeUso(
                    caso_uso_stock=caso_uso_stock,
                    caso_uso_bajo_stock=caso_uso_bajo_stock,
                    caso_uso_buscar=caso_uso_buscar,
                    caso_uso_estadisticas=caso_uso_estadisticas
                )
                
                # Ejecutar caso de uso
                resultado = caso_uso_chatbot.ejecutar(mensaje_usuario)
                
                # Guardar respuesta del asistente
                mensaje_assistant = MensajeModel.objects.create(
                    conversacion=conversacion,
                    rol='assistant',
                    contenido=resultado['respuesta'],
                    metadatos={
                        'acciones_ejecutadas': resultado.get('acciones_ejecutadas', [])
                    }
                )
                
                # Preparar respuesta
                response_data = {
                    'respuesta': resultado['respuesta'],
                    'conversacion_id': conversacion.id,
                    'mensaje_id': mensaje_assistant.id,
                    'acciones_ejecutadas': resultado.get('acciones_ejecutadas', []),
                    'sugerencias': self._generar_sugerencias(resultado['respuesta']),
                    'metadatos': {}
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': 'Error al procesar el mensaje',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generar_sugerencias(self, respuesta: str) -> list:
        """Genera sugerencias basadas en la respuesta"""
        sugerencias = []
        
        if 'stock bajo' in respuesta.lower():
            sugerencias.append("¿Quieres ver más detalles de algún producto?")
        
        if 'producto' in respuesta.lower():
            sugerencias.append("¿Necesitas buscar otro producto?")
        
        return sugerencias[:3]


class ConversacionesView(APIView):
    """
    GET: Obtiene las conversaciones del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar conversaciones del usuario"""
        conversaciones = ConversacionModel.objects.filter(
            usuario_id=request.user.id,
            activo=True
        ).order_by('-fecha_actualizacion')[:20]
        
        conversaciones_data = []
        for conv in conversaciones:
            total_mensajes = MensajeModel.objects.filter(conversacion=conv).count()
            conversaciones_data.append({
                'id': conv.id,
                'titulo': conv.titulo,
                'total_mensajes': total_mensajes,
                'fecha_creacion': conv.fecha_creacion,
                'fecha_actualizacion': conv.fecha_actualizacion
            })
        
        return Response(conversaciones_data, status=status.HTTP_200_OK)


class ConversacionDetalleView(APIView):
    """
    GET: Obtiene una conversación específica con sus mensajes
    DELETE: Elimina una conversación
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, conversacion_id):
        """Obtener conversación con mensajes"""
        try:
            conversacion = ConversacionModel.objects.get(
                id=conversacion_id,
                usuario_id=request.user.id,
                activo=True
            )
            
            mensajes = MensajeModel.objects.filter(
                conversacion=conversacion
            ).order_by('fecha_creacion')
            
            mensajes_data = [
                {
                    'id': msg.id,
                    'rol': msg.rol,
                    'contenido': msg.contenido,
                    'fecha_creacion': msg.fecha_creacion
                }
                for msg in mensajes
            ]
            
            return Response({
                'id': conversacion.id,
                'titulo': conversacion.titulo,
                'mensajes': mensajes_data,
                'total_mensajes': len(mensajes_data),
                'fecha_creacion': conversacion.fecha_creacion
            }, status=status.HTTP_200_OK)
            
        except ConversacionModel.DoesNotExist:
            return Response({
                'error': 'Conversación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, conversacion_id):
        """Eliminar conversación"""
        try:
            conversacion = ConversacionModel.objects.get(
                id=conversacion_id,
                usuario_id=request.user.id,
                activo=True
            )
            
            conversacion.activo = False
            conversacion.save()
            
            return Response({
                'mensaje': 'Conversación eliminada exitosamente'
            }, status=status.HTTP_200_OK)
            
        except ConversacionModel.DoesNotExist:
            return Response({
                'error': 'Conversación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


class NuevaConversacionView(APIView):
    """
    POST: Crea una nueva conversación vacía
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Crear nueva conversación"""
        conversacion = ConversacionModel.objects.create(
            usuario_id=request.user.id,
            titulo='Nueva conversación'
        )
        
        return Response({
            'id': conversacion.id,
            'titulo': conversacion.titulo,
            'fecha_creacion': conversacion.fecha_creacion
        }, status=status.HTTP_201_CREATED)