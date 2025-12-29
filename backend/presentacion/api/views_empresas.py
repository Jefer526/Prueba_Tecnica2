"""
Views para Empresas - CRUD COMPLETO
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from infraestructura.django_orm.models import EmpresaModel
from presentacion.api.serializers_empresas import (
    EmpresaListaSerializer,
    EmpresaDetalleSerializer,
    EmpresaCrearSerializer,
)


class EmpresaViewSet(viewsets.ModelViewSet):
    """ViewSet para Empresas - CRUD COMPLETO"""
    queryset = EmpresaModel.objects.all()
    lookup_field = 'nit'
    
    def get_permissions(self):
        """GET público, resto autenticado"""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Serializers por acción"""
        if self.action in ['create', 'update', 'partial_update']:
            return EmpresaCrearSerializer
        elif self.action == 'retrieve':
            return EmpresaDetalleSerializer
        return EmpresaListaSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar TODAS las empresas (activas e inactivas)"""
        try:
            empresas = EmpresaModel.objects.all()  # ✅ Muestra todas
            serializer = EmpresaListaSerializer(empresas, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de una empresa"""
        try:
            empresa = self.get_object()
            serializer = EmpresaDetalleSerializer(empresa)
            return Response(serializer.data)
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """Crear nueva empresa (o reactivar si existe inactiva)"""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            nit = serializer.validated_data['nit']
            
            # ✅ Verificar si existe empresa con ese NIT
            empresa_existente = EmpresaModel.objects.filter(nit=nit).first()
            
            if empresa_existente:
                # Si existe y está activa → Error
                if empresa_existente.activo:
                    return Response(
                        {'error': f'Ya existe una empresa activa con NIT {nit}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Si existe pero está inactiva → Reactivar y actualizar
                empresa_existente.activo = True
                empresa_existente.nombre = serializer.validated_data['nombre']
                empresa_existente.direccion = serializer.validated_data.get('direccion', '')
                empresa_existente.telefono = serializer.validated_data.get('telefono', '')
                empresa_existente.save()
                
                response_serializer = EmpresaDetalleSerializer(empresa_existente)
                return Response(
                    {
                        'mensaje': 'Empresa reactivada y actualizada exitosamente',
                        'empresa': response_serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            
            # Si no existe → Crear nueva
            empresa = EmpresaModel.objects.create(
                nit=nit,
                nombre=serializer.validated_data['nombre'],
                direccion=serializer.validated_data.get('direccion', ''),
                telefono=serializer.validated_data.get('telefono', ''),
            )
            
            response_serializer = EmpresaDetalleSerializer(empresa)
            return Response(
                {
                    'mensaje': 'Empresa creada exitosamente',
                    'empresa': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """Actualizar empresa completa (PUT)"""
        try:
            empresa = self.get_object()
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Actualizar campos
            empresa.nombre = serializer.validated_data['nombre']
            empresa.direccion = serializer.validated_data.get('direccion', '')
            empresa.telefono = serializer.validated_data.get('telefono', '')
            empresa.save()
            
            response_serializer = EmpresaDetalleSerializer(empresa)
            return Response(
                {
                    'mensaje': 'Empresa actualizada exitosamente',
                    'empresa': response_serializer.data
                }
            )
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def partial_update(self, request, *args, **kwargs):
        """Actualizar empresa parcial (PATCH)"""
        try:
            empresa = self.get_object()
            
            # Actualizar solo campos enviados
            if 'nombre' in request.data:
                empresa.nombre = request.data['nombre']
            if 'direccion' in request.data:
                empresa.direccion = request.data['direccion']
            if 'telefono' in request.data:
                empresa.telefono = request.data['telefono']
            
            empresa.save()
            
            response_serializer = EmpresaDetalleSerializer(empresa)
            return Response(
                {
                    'mensaje': 'Empresa actualizada exitosamente',
                    'empresa': response_serializer.data
                }
            )
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar empresa (DELETE) - HARD DELETE (elimina físicamente)"""
        try:
            empresa = self.get_object()
            
            # Verificar si tiene productos asociados
            if empresa.productos.exists():
                return Response(
                    {'error': 'No se puede eliminar una empresa con productos asociados'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # ✅ HARD DELETE - Eliminar físicamente
            nit_eliminado = empresa.nit
            empresa.delete()
            
            return Response(
                {'mensaje': f'Empresa {nit_eliminado} eliminada permanentemente'},
                status=status.HTTP_200_OK
            )
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post', 'patch'])
    def inactivar(self, request, nit=None):
        """Inactivar empresa (POST /empresas/{nit}/inactivar/)"""
        try:
            empresa = self.get_object()
            
            if not empresa.activo:
                return Response(
                    {'error': 'La empresa ya está inactiva'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            empresa.activo = False
            empresa.save()
            
            return Response(
                {'mensaje': 'Empresa inactivada exitosamente'},
                status=status.HTTP_200_OK
            )
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al inactivar empresa: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post', 'patch'])
    def activar(self, request, nit=None):
        """Activar empresa (POST /empresas/{nit}/activar/)"""
        try:
            empresa = self.get_object()
            
            if empresa.activo:
                return Response(
                    {'error': 'La empresa ya está activa'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            empresa.activo = True
            empresa.save()
            
            return Response(
                {'mensaje': 'Empresa activada exitosamente'},
                status=status.HTTP_200_OK
            )
        except EmpresaModel.DoesNotExist:
            return Response({'error': 'Empresa no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error al activar empresa: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)