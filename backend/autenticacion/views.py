from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from .models import Usuario
from .serializers import (
    RegistroUsuarioSerializer,
    LoginSerializer,
    UsuarioSerializer,
    CambiarContrasenaSerializer
)

class RegistroUsuarioView(generics.CreateAPIView):
    """Vista para registrar nuevos usuarios"""
    
    queryset = Usuario.objects.all()
    serializer_class = RegistroUsuarioSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(usuario)
        
        return Response({
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': UsuarioSerializer(usuario).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Vista para iniciar sesión"""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        usuario = serializer.validated_data['usuario']
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(usuario)
        
        return Response({
            'mensaje': 'Inicio de sesión exitoso',
            'usuario': UsuarioSerializer(usuario).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Vista para cerrar sesión"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({
                'mensaje': 'Sesión cerrada exitosamente'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Error al cerrar sesión'
            }, status=status.HTTP_400_BAD_REQUEST)


class PerfilUsuarioView(generics.RetrieveUpdateAPIView):
    """Vista para ver y actualizar el perfil del usuario"""
    
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class CambiarContrasenaView(APIView):
    """Vista para cambiar la contraseña del usuario"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = CambiarContrasenaSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Cambiar contraseña
        usuario = request.user
        usuario.set_password(serializer.validated_data['contrasena_nueva'])
        usuario.save()
        
        return Response({
            'mensaje': 'Contraseña cambiada exitosamente'
        }, status=status.HTTP_200_OK)


class ListaUsuariosView(generics.ListAPIView):
    """Vista para listar todos los usuarios (solo administradores)"""
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Solo administradores pueden ver todos los usuarios
        if self.request.user.tiene_permiso_administrador():
            return Usuario.objects.all()
        # Usuarios externos solo ven su propio perfil
        return Usuario.objects.filter(id=self.request.user.id)