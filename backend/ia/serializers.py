from rest_framework import serializers
from .models import ConversacionIA, MensajeIA, AccionIA


class MensajeIASerializer(serializers.ModelSerializer):
    """Serializer para mensajes del chatbot"""
    
    class Meta:
        model = MensajeIA
        fields = [
            'id',
            'rol',
            'contenido',
            'metadatos',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']


class AccionIASerializer(serializers.ModelSerializer):
    """Serializer para acciones ejecutadas por el chatbot"""
    
    class Meta:
        model = AccionIA
        fields = [
            'id',
            'tipo_accion',
            'parametros',
            'resultado',
            'exitoso',
            'fecha_ejecucion',
        ]
        read_only_fields = ['id', 'fecha_ejecucion']


class ConversacionIASerializer(serializers.ModelSerializer):
    """Serializer para conversaciones del chatbot"""
    
    mensajes = MensajeIASerializer(many=True, read_only=True)
    total_mensajes = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversacionIA
        fields = [
            'id',
            'titulo',
            'mensajes',
            'total_mensajes',
            'fecha_creacion',
            'fecha_actualizacion',
            'activo',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_total_mensajes(self, obj):
        return obj.mensajes.count()


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
    acciones_ejecutadas = serializers.ListField(child=serializers.CharField(), default=list)
    sugerencias = serializers.ListField(child=serializers.CharField(), default=list)
    metadatos = serializers.DictField(default=dict)
