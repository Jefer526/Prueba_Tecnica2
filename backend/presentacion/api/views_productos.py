"""
Views para Productos - COMPLETO
Muestra todos (activos e inactivos), Hard Delete, empresa_nit
"""
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from infraestructura.django_orm.models import ProductoModel, EmpresaModel, InventarioModel
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
        """Listar TODOS los productos (activos e inactivos)"""
        try:
            productos = ProductoModel.objects.select_related('empresa').all()  # ✅ Todos
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
        """Crear nuevo producto con código automático"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Verificar que la empresa existe
            empresa_nit = serializer.validated_data.get('empresa_nit')
            if not empresa_nit:
                return Response(
                    {'error': 'empresa_nit es requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                empresa = EmpresaModel.objects.get(nit=empresa_nit, activo=True)
            except EmpresaModel.DoesNotExist:
                return Response(
                    {'error': f'No existe una empresa activa con NIT {empresa_nit}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ Generar código automático según categoría
            categoria = serializer.validated_data.get('categoria', 'OTROS')
            prefijo_map = {
                'TECNOLOGIA': 'TE',
                'ROPA': 'RO',
                'ALIMENTOS': 'AL',
                'HOGAR': 'HO',
                'DEPORTES': 'DE',
                'OTROS': 'OT'
            }
            prefijo = prefijo_map.get(categoria, 'OT')
            
            # Obtener último producto con ese prefijo
            ultimo = ProductoModel.objects.filter(
                codigo__startswith=prefijo
            ).order_by('-codigo').first()
            
            if ultimo:
                try:
                    numero = int(ultimo.codigo[2:]) + 1
                except ValueError:
                    numero = 1
            else:
                numero = 1
            
            codigo = f"{prefijo}{numero:04d}"  # TE0001, TE0002...
            
            # ✅ Calcular precios en otras monedas (tasas de cambio fijas)
            precio_usd = serializer.validated_data['precio_usd']
            precio_cop = precio_usd * Decimal('4200')
            precio_eur = precio_usd * Decimal('0.92')
            
            # Crear producto
            producto = ProductoModel.objects.create(
                codigo=codigo,
                nombre=serializer.validated_data['nombre'],
                descripcion=serializer.validated_data.get('descripcion', ''),
                precio_usd=precio_usd,
                precio_cop=precio_cop,
                precio_eur=precio_eur,
                categoria=categoria,
                empresa=empresa,
                activo=True
            )
            
            # ✅ Crear registro de inventario automáticamente
            InventarioModel.objects.create(
                producto=producto,
                empresa=empresa,
                stock_actual=0,
                stock_minimo=10,
                stock_maximo=100,
                requiere_reorden=True
            )
            
            response_serializer = ProductoDetalleSerializer(producto)
            return Response(
                {
                    'mensaje': 'Producto creado exitosamente',
                    'producto': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Actualizar producto completo (PUT)"""
        try:
            producto = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Actualizar campos
            producto.nombre = serializer.validated_data['nombre']
            producto.descripcion = serializer.validated_data.get('descripcion', '')
            
            # ✅ Actualizar precio y recalcular otras monedas
            precio_usd = serializer.validated_data['precio_usd']
            producto.precio_usd = precio_usd
            producto.precio_cop = precio_usd * Decimal('4200')
            producto.precio_eur = precio_usd * Decimal('0.92')
            
            if 'categoria' in serializer.validated_data:
                producto.categoria = serializer.validated_data['categoria']
            
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
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar producto parcial (PATCH)"""
        try:
            producto = self.get_object()
            
            # Actualizar solo campos enviados
            if 'nombre' in request.data:
                producto.nombre = request.data['nombre']
            if 'descripcion' in request.data:
                producto.descripcion = request.data['descripcion']
            if 'precio_usd' in request.data:
                precio_usd = Decimal(str(request.data['precio_usd']))
                producto.precio_usd = precio_usd
                producto.precio_cop = precio_usd * Decimal('4200')
                producto.precio_eur = precio_usd * Decimal('0.92')
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
        """Eliminar producto (DELETE) - HARD DELETE"""
        try:
            producto = self.get_object()
            
            # Verificar si tiene inventario
            try:
                inventario = InventarioModel.objects.get(producto=producto)
                if inventario.stock_actual > 0:
                    return Response(
                        {'error': 'No se puede eliminar un producto con stock en inventario'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Eliminar inventario también
                inventario.delete()
            except InventarioModel.DoesNotExist:
                pass
            
            # ✅ HARD DELETE - Eliminar físicamente
            codigo_eliminado = producto.codigo
            producto.delete()
            
            return Response(
                {'mensaje': f'Producto {codigo_eliminado} eliminado permanentemente'},
                status=status.HTTP_200_OK
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
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
            
            print(f"✅ Producto {producto.codigo} inactivado")
            
            return Response(
                {'mensaje': 'Producto inactivado exitosamente'},
                status=status.HTTP_200_OK
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
            
            print(f"✅ Producto {producto.codigo} activado")
            
            return Response(
                {'mensaje': 'Producto activado exitosamente'},
                status=status.HTTP_200_OK
            )
        except ProductoModel.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)