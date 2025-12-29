"""
Serializers de Autenticación - Capa de Presentación
DTOs para entrada y salida de endpoints de autenticación
"""
from rest_framework import serializers


# ==================== REGISTRO ====================

class RegistrarUsuarioSerializer(serializers.Serializer):
    """Serializer para registrar un nuevo usuario"""
    nombre = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    rol = serializers.ChoiceField(
        choices=[('ADMINISTRADOR', 'Administrador'), ('EXTERNO', 'Externo')],
        default='EXTERNO'
    )


class RegistrarUsuarioResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de registro"""
    usuario = serializers.DictField()
    mensaje = serializers.CharField()


# ==================== LOGIN ====================

class IniciarSesionSerializer(serializers.Serializer):
    """Serializer para iniciar sesión"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class IniciarSesionResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de login"""
    usuario = serializers.DictField()
    access = serializers.CharField()  # Token JWT
    refresh = serializers.CharField()  # Token de refresh
    mensaje = serializers.CharField()


# ==================== PERFIL ====================

class UsuarioSerializer(serializers.Serializer):
    """Serializer para datos de usuario"""
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField()
    email = serializers.EmailField()
    rol = serializers.CharField()
    activo = serializers.BooleanField()
    fecha_creacion = serializers.DateTimeField(read_only=True, required=False)
