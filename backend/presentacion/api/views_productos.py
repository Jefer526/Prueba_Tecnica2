"""
Views para Productos - ULTRA SIMPLIFICADO
Solo usa caso de uso para CREAR, el resto directo con modelos
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from infraestructura.django_orm.models import ProductoModel, EmpresaModel
from presentacion.api.serializers_productos import (
    ProductoListaSerializer,
    ProductoDetalleSerializer,
    ProductoCrearSerializer,
)


class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para Productos - CRUD COMPLETO"""
    queryset = ProductoModel.objects.select_related('empresa').all()
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductoCrearSerializer
        elif self.action == 'retrieve':
            return ProductoDetalleSerializer
        return ProductoListaSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar productos activos"""
        try:
            productos = ProductoModel.objects.filter(activo=True).select_related('empresa')
            serializer = ProductoListaSerializer(productos, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de un producto"""
        try:
            producto = self.get_object()
            serializer = ProductoDetalleSerializer(producto)
            return Response(serializer.data)
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """Crear nuevo producto - USA CASO DE USO"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar que la empresa existe
            empresa_nit = serializer.validated_data['empresa_nit']
            try:
                empresa = EmpresaModel.objects.get(nit=empresa_nit, activo=True)
            except EmpresaModel.DoesNotExist:
                return Response(
                    {'error': f'No existe una empresa activa con NIT {empresa_nit}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Usar caso de uso de crear_producto.py
            try:
                from aplicacion.casos_uso.crear_producto import CrearProductoCasoDeUso
                from infraestructura.django_orm.repositorios import (
                    RepositorioProductosDjango,
                    RepositorioEmpresasDjango,
                )
                
                repositorio_productos = RepositorioProductosDjango()
                repositorio_empresas = RepositorioEmpresasDjango()
                
                caso_uso = CrearProductoCasoDeUso(
                    repositorio_productos,
                    repositorio_empresas
                )
                
                producto = caso_uso.ejecutar(
                    nombre=serializer.validated_data['nombre'],
                    descripcion=serializer.validated_data.get('descripcion', ''),
                    precio_usd=float(serializer.validated_data['precio_usd']),
                    categoria=serializer.validated_data['categoria'],
                    empresa_nit=empresa_nit
                )
                
                producto_model = ProductoModel.objects.get(id=producto.id)
                
            except ImportError:
                # Si el caso de uso no existe, crear directamente
                # Generar código automático
                categoria = serializer.validated_data['categoria']
                prefijo_map = {
                    'TECNOLOGIA': 'TE',
                    'ROPA': 'RO',
                    'ALIMENTOS': 'AL',
                    'HOGAR': 'HO',
                    'DEPORTES': 'DE',
                    'OTROS': 'OT'
                }
                prefijo = prefijo_map.get(categoria, 'OT')
                
                # Obtener último número
                productos_categoria = ProductoModel.objects.filter(
                    codigo__startswith=prefijo
                ).order_by('-codigo')
                
                if productos_categoria.exists():
                    ultimo_codigo = productos_categoria.first().codigo
                    ultimo_numero = int(ultimo_codigo[2:])
                    siguiente_numero = ultimo_numero + 1
                else:
                    siguiente_numero = 1
                
                codigo = f"{prefijo}{siguiente_numero:04d}"
                
                # Crear producto
                producto_model = ProductoModel.objects.create(
                    codigo=codigo,
                    nombre=serializer.validated_data['nombre'],
                    descripcion=serializer.validated_data.get('descripcion', ''),
                    precio_usd=serializer.validated_data['precio_usd'],
                    categoria=categoria,
                    empresa=empresa
                )
            
            response_serializer = ProductoDetalleSerializer(producto_model)
            return Response(
                {
                    'mensaje': 'Producto creado exitosamente',
                    'producto': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Actualizar producto completo (PUT)"""
        try:
            producto = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            producto.nombre = serializer.validated_data['nombre']
            producto.descripcion = serializer.validated_data.get('descripcion', '')
            producto.precio_usd = serializer.validated_data['precio_usd']
            producto.categoria = serializer.validated_data['categoria']
            producto.calcular_precios()
            producto.save()
            
            response_serializer = ProductoDetalleSerializer(producto)
            return Response(
                {
                    'mensaje': 'Producto actualizado exitosamente',
                    'producto': response_serializer.data
                }
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar producto parcial (PATCH)"""
        try:
            producto = self.get_object()
            
            if 'nombre' in request.data:
                producto.nombre = request.data['nombre']
            if 'descripcion' in request.data:
                producto.descripcion = request.data['descripcion']
            if 'precio_usd' in request.data:
                producto.precio_usd = request.data['precio_usd']
                producto.calcular_precios()
            if 'categoria' in request.data:
                producto.categoria = request.data['categoria']
            
            producto.save()
            
            response_serializer = ProductoDetalleSerializer(producto)
            return Response(
                {
                    'mensaje': 'Producto actualizado exitosamente',
                    'producto': response_serializer.data
                }
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar producto (DELETE) - Soft delete"""
        try:
            producto = self.get_object()
            
            # Verificar inventario
            if hasattr(producto, 'registro_inventario') and producto.registro_inventario.cantidad > 0:
                return Response(
                    {'error': 'No se puede eliminar un producto con inventario'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            producto.activo = False
            producto.save()
            
            return Response(
                {'mensaje': 'Producto eliminado exitosamente'},
                status=status.HTTP_200_OK
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def inactivar(self, request, pk=None):
        """Inactivar producto"""
        try:
            producto = self.get_object()
            if not producto.activo:
                return Response(
                    {'error': 'El producto ya está inactivo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            producto.activo = False
            producto.save()
            return Response({'mensaje': 'Producto inactivado exitosamente'}, status=status.HTTP_200_OK)
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Activar producto"""
        try:
            producto = self.get_object()
            if producto.activo:
                return Response(
                    {'error': 'El producto ya está activo'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            producto.activo = True
            producto.save()
            return Response({'mensaje': 'Producto activado exitosamente'}, status=status.HTTP_200_OK)
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
