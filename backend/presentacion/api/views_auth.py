"""
Vistas de Autenticación - Capa de Presentación
Coordinan HTTP y delegan lógica a los casos de uso
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from presentacion.api.serializers_auth import (
    RegistrarUsuarioSerializer,
    RegistrarUsuarioResponseSerializer,
    IniciarSesionSerializer,
    IniciarSesionResponseSerializer,
    UsuarioSerializer,
)

# Importar casos de uso
from aplicacion.casos_uso.autenticacion import (
    RegistrarUsuarioCasoDeUso,
    IniciarSesionCasoDeUso,
    ObtenerPerfilCasoDeUso,
)

# Importar repositorios
from infraestructura.django_orm.repositorio_usuario import RepositorioUsuarioDjango

# Importar excepciones del dominio
from dominio.excepciones.excepciones_negocio import (
    EmailDuplicado,
    UsuarioNoEncontrado,
    CredencialesInvalidas,
    DatosInvalidos,
    ExcepcionDominio,
)


class RegistrarUsuarioView(APIView):
    """
    POST: Registra un nuevo usuario
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Registrar usuario usando el caso de uso"""
        serializer = RegistrarUsuarioSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Instanciar repositorio
            repo_usuario = RepositorioUsuarioDjango()
            
            # Instanciar caso de uso
            caso_uso = RegistrarUsuarioCasoDeUso(
                repositorio_usuario=repo_usuario
            )
            
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(serializer.validated_data)
            
            # Serializar respuesta
            response_serializer = RegistrarUsuarioResponseSerializer(resultado)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except EmailDuplicado as e:
            return Response({
                'error': 'Email duplicado',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DatosInvalidos as e:
            return Response({
                'error': 'Datos inválidos',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except ExcepcionDominio as e:
            return Response({
                'error': 'Error de negocio',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'error': 'Error al registrar usuario',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class IniciarSesionView(APIView):
    """
    POST: Inicia sesión y genera tokens JWT
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Login usando el caso de uso"""
        serializer = IniciarSesionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Instanciar repositorio
            repo_usuario = RepositorioUsuarioDjango()
            
            # Instanciar caso de uso
            caso_uso = IniciarSesionCasoDeUso(
                repositorio_usuario=repo_usuario
            )
            
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(serializer.validated_data)
            
            # Generar tokens JWT
            refresh = RefreshToken()
            refresh['user_id'] = resultado['usuario']['id']
            refresh['email'] = resultado['usuario']['email']
            refresh['rol'] = resultado['usuario']['rol']
            
            # Agregar tokens al resultado
            resultado['access'] = str(refresh.access_token)
            resultado['refresh'] = str(refresh)
            
            # Serializar respuesta
            response_serializer = IniciarSesionResponseSerializer(resultado)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )
            
        except UsuarioNoEncontrado as e:
            return Response({
                'error': 'Usuario no encontrado',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        except CredencialesInvalidas as e:
            return Response({
                'error': 'Credenciales inválidas',
                'detalle': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        except Exception as e:
            return Response({
                'error': 'Error al iniciar sesión',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ObtenerPerfilView(APIView):
    """
    GET: Obtiene el perfil del usuario autenticado
    Requiere token JWT válido
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Obtener perfil del usuario autenticado"""
        try:
            # Obtener ID del usuario del token JWT
            usuario_id = request.user.id
            
            # Instanciar repositorio
            repo_usuario = RepositorioUsuarioDjango()
            
            # Instanciar caso de uso
            caso_uso = ObtenerPerfilCasoDeUso(
                repositorio_usuario=repo_usuario
            )
            
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(usuario_id)
            
            # Serializar respuesta
            serializer = UsuarioSerializer(resultado['usuario'])
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except UsuarioNoEncontrado as e:
            return Response({
                'error': 'Usuario no encontrado',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({
                'error': 'Error al obtener perfil',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
