from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Producto
from .serializers import ProductoSerializer, ProductoCrearSerializer, ProductoListaSerializer
from empresas.views import EsAdministrador

class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar productos"""
    
    queryset = Producto.objects.all()
    permission_classes = [EsAdministrador]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['empresa', 'activo']
    search_fields = ['codigo', 'nombre', 'caracteristicas']
    ordering_fields = ['nombre', 'precio_usd', 'fecha_creacion']
    ordering = ['nombre']
    lookup_field = 'codigo'  # Usar código en lugar de pk
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'create':
            return ProductoCrearSerializer
        elif self.action == 'list':
            return ProductoListaSerializer
        return ProductoSerializer
    
    def get_queryset(self):
        """Filtra los productos según el usuario"""
        queryset = Producto.objects.all()
        
        # Si el usuario es externo, solo mostrar productos activos
        if not self.request.user.tiene_permiso_administrador():
            queryset = queryset.filter(activo=True)
        
        # Filtrar por empresa si se especifica
        empresa_nit = self.request.query_params.get('empresa_nit', None)
        if empresa_nit:
            queryset = queryset.filter(empresa__nit=empresa_nit)
        
        # Filtrar por rango de precios
        precio_min = self.request.query_params.get('precio_min', None)
        precio_max = self.request.query_params.get('precio_max', None)
        
        if precio_min:
            queryset = queryset.filter(precio_usd__gte=precio_min)
        if precio_max:
            queryset = queryset.filter(precio_usd__lte=precio_max)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Crea un nuevo producto"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar con serializer completo
        producto = Producto.objects.get(pk=serializer.instance.pk)
        
        return Response({
            'mensaje': 'Producto creado exitosamente',
            'producto': ProductoSerializer(producto, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Actualiza un producto"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'mensaje': 'Producto actualizado exitosamente',
            'producto': ProductoSerializer(instance, context={'request': request}).data
        })
    
    def destroy(self, request, *args, **kwargs):
        """Elimina permanentemente un producto de la base de datos"""
        instance = self.get_object()
        
        # Guardar el nombre para el mensaje de respuesta
        nombre_producto = instance.nombre
        
        # Eliminar de verdad (hard delete)
        instance.delete()
        
        return Response({
            'mensaje': f'Producto {nombre_producto} eliminado permanentemente'
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, codigo=None):
        """Activa o desactiva un producto (toggle)"""
        producto = self.get_object()
        
        # Toggle: invertir el estado actual
        producto.activo = not producto.activo
        producto.save()
        
        estado = 'activado' if producto.activo else 'desactivado'
        
        return Response({
            'mensaje': f'Producto {estado} exitosamente',
            'producto': ProductoSerializer(producto, context={'request': request}).data
        })
    
    @action(detail=False, methods=['get'])
    def por_empresa(self, request):
        """Lista productos agrupados por empresa"""
        empresa_nit = request.query_params.get('nit', None)
        
        if not empresa_nit:
            return Response({
                'error': 'Debe proporcionar el NIT de la empresa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        productos = self.get_queryset().filter(empresa__nit=empresa_nit)
        serializer = ProductoListaSerializer(productos, many=True)
        
        return Response({
            'empresa_nit': empresa_nit,
            'total_productos': productos.count(),
            'productos': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def actualizar_precios(self, request, codigo=None):
        """Actualiza los precios en todas las monedas basado en USD"""
        producto = self.get_object()
        
        # Recalcular precios
        producto.calcular_precios_monedas()
        producto.save()
        
        return Response({
            'mensaje': 'Precios actualizados exitosamente',
            'producto': ProductoSerializer(producto, context={'request': request}).data
        })