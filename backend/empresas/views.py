from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Empresa
from .serializers import EmpresaSerializer, EmpresaListaSerializer

class EsAdministrador(permissions.BasePermission):
    """Permiso personalizado para verificar si el usuario es administrador"""
    
    def has_permission(self, request, view):
        # Permitir lectura a usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Permitir escritura solo a administradores
        return request.user and request.user.is_authenticated and request.user.tiene_permiso_administrador()


class EmpresaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar empresas"""
    
    queryset = Empresa.objects.all()
    permission_classes = [EsAdministrador]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['activo']
    search_fields = ['nit', 'nombre', 'telefono']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'list':
            return EmpresaListaSerializer
        return EmpresaSerializer
    
    def get_queryset(self):
        """Filtra las empresas según el usuario"""
        queryset = Empresa.objects.all()
        
        # Si el usuario es externo, solo mostrar empresas activas
        if not self.request.user.tiene_permiso_administrador():
            queryset = queryset.filter(activo=True)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crea una nueva empresa"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'mensaje': 'Empresa creada exitosamente',
            'empresa': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Actualiza una empresa"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'mensaje': 'Empresa actualizada exitosamente',
            'empresa': serializer.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina (desactiva) una empresa"""
        instance = self.get_object()
        
        # En lugar de eliminar, desactivar
        instance.activo = False
        instance.save()
        
        return Response({
            'mensaje': 'Empresa desactivada exitosamente'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activa una empresa desactivada"""
        empresa = self.get_object()
        empresa.activo = True
        empresa.save()
        
        return Response({
            'mensaje': 'Empresa activada exitosamente',
            'empresa': EmpresaSerializer(empresa).data
        })
    
    @action(detail=True, methods=['get'])
    def estadisticas(self, request, pk=None):
        """Obtiene estadísticas de la empresa"""
        empresa = self.get_object()
        
        estadisticas = {
            'total_productos': empresa.total_productos(),
            'valor_total_inventario': empresa.valor_total_inventario(),
            'productos_activos': empresa.productos.filter(activo=True).count(),
            'productos_inactivos': empresa.productos.filter(activo=False).count(),
        }
        
        return Response(estadisticas)