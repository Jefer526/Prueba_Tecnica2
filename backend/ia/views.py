from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from django.db import transaction

from .models import ConversacionIA, MensajeIA, AccionIA
from .serializers import (
    ConversacionIASerializer,
    MensajeIASerializer,
    ChatRequestSerializer,
    ChatResponseSerializer
)
from .chatbot_service import ChatbotService


class IAViewSet(viewsets.ViewSet):
    """ViewSet para el chatbot de IA"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chatbot_service = ChatbotService()
    
    @action(detail=False, methods=['post'])
    def chat(self, request):
        """
        Endpoint principal del chatbot
        
        POST /api/ia/chat/
        {
            "mensaje": "¿Qué productos están bajos de stock?",
            "conversacion_id": 1  // Opcional
        }
        """
        # Validar request
        serializer = ChatRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        mensaje_usuario = serializer.validated_data['mensaje']
        conversacion_id = serializer.validated_data.get('conversacion_id')
        
        try:
            with transaction.atomic():
                # Obtener o crear conversación
                if conversacion_id:
                    try:
                        conversacion = ConversacionIA.objects.get(
                            id=conversacion_id,
                            usuario=request.user,
                            activo=True
                        )
                    except ConversacionIA.DoesNotExist:
                        # Crear nueva si no existe
                        conversacion = ConversacionIA.objects.create(
                            usuario=request.user,
                            titulo=mensaje_usuario[:50]
                        )
                else:
                    # Crear nueva conversación
                    conversacion = ConversacionIA.objects.create(
                        usuario=request.user,
                        titulo=mensaje_usuario[:50]
                    )
                
                # Guardar mensaje del usuario
                mensaje_user = MensajeIA.objects.create(
                    conversacion=conversacion,
                    rol='user',
                    contenido=mensaje_usuario
                )
                
                # Obtener historial de la conversación
                mensajes_anteriores = MensajeIA.objects.filter(
                    conversacion=conversacion
                ).order_by('fecha_creacion')
                
                # Preparar mensajes para OpenAI
                mensajes_openai = [
                    {
                        "role": msg.rol,
                        "content": msg.contenido
                    }
                    for msg in mensajes_anteriores
                ]
                
                # Generar respuesta
                resultado = self.chatbot_service.generar_respuesta(mensajes_openai)
                
                if not resultado['exito']:
                    return Response(
                        {'error': resultado.get('error', 'Error desconocido')},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # Guardar respuesta del asistente
                mensaje_assistant = MensajeIA.objects.create(
                    conversacion=conversacion,
                    rol='assistant',
                    contenido=resultado['respuesta'],
                    metadatos={
                        'tokens_usados': resultado.get('tokens_usados', 0),
                        'acciones_ejecutadas': resultado.get('acciones_ejecutadas', [])
                    }
                )
                
                # Registrar acciones ejecutadas
                for accion in resultado.get('acciones_ejecutadas', []):
                    AccionIA.objects.create(
                        mensaje=mensaje_assistant,
                        tipo_accion=accion if accion in dict(AccionIA.TIPOS_ACCION) else 'consulta_stock',
                        parametros={},
                        resultado={},
                        exitoso=True
                    )
                
                # Preparar respuesta
                response_data = {
                    'respuesta': resultado['respuesta'],
                    'conversacion_id': conversacion.id,
                    'mensaje_id': mensaje_assistant.id,
                    'acciones_ejecutadas': resultado.get('acciones_ejecutadas', []),
                    'sugerencias': self._generar_sugerencias(resultado['respuesta']),
                    'metadatos': {
                        'tokens_usados': resultado.get('tokens_usados', 0)
                    }
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response(
                {'error': f'Error al procesar el mensaje: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def conversaciones(self, request):
        """
        Obtiene las conversaciones del usuario
        
        GET /api/ia/conversaciones/
        """
        conversaciones = ConversacionIA.objects.filter(
            usuario=request.user,
            activo=True
        ).prefetch_related('mensajes')[:20]
        
        serializer = ConversacionIASerializer(conversaciones, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conversacion(self, request, pk=None):
        """
        Obtiene una conversación específica con todos sus mensajes
        
        GET /api/ia/conversacion/{id}/
        """
        try:
            conversacion = ConversacionIA.objects.prefetch_related('mensajes').get(
                id=pk,
                usuario=request.user,
                activo=True
            )
            serializer = ConversacionIASerializer(conversacion)
            return Response(serializer.data)
        except ConversacionIA.DoesNotExist:
            return Response(
                {'error': 'Conversación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['delete'])
    def eliminar_conversacion(self, request, pk=None):
        """
        Elimina (desactiva) una conversación
        
        DELETE /api/ia/conversacion/{id}/
        """
        try:
            conversacion = ConversacionIA.objects.get(
                id=pk,
                usuario=request.user,
                activo=True
            )
            conversacion.activo = False
            conversacion.save()
            
            return Response(
                {'mensaje': 'Conversación eliminada exitosamente'},
                status=status.HTTP_200_OK
            )
        except ConversacionIA.DoesNotExist:
            return Response(
                {'error': 'Conversación no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def nueva_conversacion(self, request):
        """
        Crea una nueva conversación vacía
        
        POST /api/ia/nueva_conversacion/
        """
        conversacion = ConversacionIA.objects.create(
            usuario=request.user,
            titulo='Nueva conversación'
        )
        
        serializer = ConversacionIASerializer(conversacion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def _generar_sugerencias(self, respuesta: str) -> list:
        """Genera sugerencias basadas en la respuesta"""
        sugerencias = []
        
        # Sugerencias básicas
        if 'stock bajo' in respuesta.lower() or 'reorden' in respuesta.lower():
            sugerencias.append("¿Quieres que genere un PDF con los productos críticos?")
            sugerencias.append("¿Deseas ver el historial de movimientos de algún producto?")
        
        if 'producto' in respuesta.lower():
            sugerencias.append("¿Necesitas más detalles sobre algún producto?")
        
        if 'movimiento' in respuesta.lower():
            sugerencias.append("¿Quieres registrar un nuevo movimiento?")
        
        # Limitar a 3 sugerencias
        return sugerencias[:3]
