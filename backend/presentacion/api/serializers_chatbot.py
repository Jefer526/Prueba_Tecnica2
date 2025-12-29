"""
Serializers del Chatbot - Capa de Presentación
DTOs para entrada y salida de endpoints del chatbot
"""
from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Serializer para validar requests al chatbot"""
    
    mensaje = serializers.CharField(required=True, max_length=2000)
    conversacion_id = serializers.IntegerField(required=False, allow_null=True)
    incluir_contexto = serializers.BooleanField(default=True)
    
    def validate_mensaje(self, value):
        """Valida que el mensaje no esté vacío"""
        if not value.strip():
            raise serializers.ValidationError("El mensaje no puede estar vacío")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer para respuestas del chatbot"""
    
    respuesta = serializers.CharField()
    conversacion_id = serializers.IntegerField()
    mensaje_id = serializers.IntegerField()
    acciones_ejecutadas = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    sugerencias = serializers.ListField(
        child=serializers.CharField(),
        default=list
    )
    metadatos = serializers.DictField(default=dict)


class MensajeSerializer(serializers.Serializer):
    """Serializer para mensajes del chatbot"""
    
    id = serializers.IntegerField(read_only=True)
    rol = serializers.CharField()
    contenido = serializers.CharField()
    fecha_creacion = serializers.DateTimeField(read_only=True)


class ConversacionSerializer(serializers.Serializer):
    """Serializer para conversaciones del chatbot"""
    
    id = serializers.IntegerField(read_only=True)
    titulo = serializers.CharField()
    mensajes = MensajeSerializer(many=True, read_only=True)
    total_mensajes = serializers.IntegerField(read_only=True)
    fecha_creacion = serializers.DateTimeField(read_only=True)
    fecha_actualizacion = serializers.DateTimeField(read_only=True)
