from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Usuario

class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevos usuarios"""
    
    contrasena = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirmar_contrasena = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Usuario
        fields = [
            'correo',
            'nombre_completo',
            'contrasena',
            'confirmar_contrasena',
            'tipo_usuario',
        ]
    
    def validate(self, datos):
        """Valida que las contraseñas coincidan"""
        if datos['contrasena'] != datos['confirmar_contrasena']:
            raise serializers.ValidationError({
                'confirmar_contrasena': 'Las contraseñas no coinciden'
            })
        return datos
    
    def create(self, datos_validados):
        """Crea un nuevo usuario"""
        datos_validados.pop('confirmar_contrasena')
        
        # Si el tipo es administrador, activar flag correspondiente
        if datos_validados.get('tipo_usuario') == 'ADMINISTRADOR':
            datos_validados['es_administrador'] = True
        
        usuario = Usuario.objects.create_user(**datos_validados)
        return usuario


class LoginSerializer(serializers.Serializer):
    """Serializer para login de usuarios"""
    
    correo = serializers.EmailField()
    contrasena = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, datos):
        """Valida las credenciales del usuario"""
        correo = datos.get('correo')
        contrasena = datos.get('contrasena')
        
        if correo and contrasena:
            usuario = authenticate(
                request=self.context.get('request'),
                username=correo,
                password=contrasena
            )
            
            if not usuario:
                raise serializers.ValidationError(
                    'No se pudo iniciar sesión con las credenciales proporcionadas',
                    code='authorization'
                )
            
            if not usuario.esta_activo:
                raise serializers.ValidationError(
                    'La cuenta de usuario está desactivada',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Debe incluir "correo" y "contrasena"',
                code='authorization'
            )
        
        datos['usuario'] = usuario
        return datos


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información del usuario"""
    
    class Meta:
        model = Usuario
        fields = [
            'id',
            'correo',
            'nombre_completo',
            'tipo_usuario',
            'es_administrador',
            'esta_activo',
            'fecha_creacion',
        ]
        read_only_fields = ['id', 'fecha_creacion']


class CambiarContrasenaSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    
    contrasena_actual = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    contrasena_nueva = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirmar_contrasena_nueva = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    
    def validate(self, datos):
        """Valida que las contraseñas coincidan"""
        if datos['contrasena_nueva'] != datos['confirmar_contrasena_nueva']:
            raise serializers.ValidationError({
                'confirmar_contrasena_nueva': 'Las contraseñas no coinciden'
            })
        return datos
    
    def validate_contrasena_actual(self, valor):
        """Valida que la contraseña actual sea correcta"""
        usuario = self.context['request'].user
        if not usuario.check_password(valor):
            raise serializers.ValidationError('La contraseña actual es incorrecta')
        return valor