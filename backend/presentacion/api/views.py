"""
Vistas de la API - Capa de Presentación
Coordinan HTTP y delegan lógica a los casos de uso
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from presentacion.api.serializers import (
    EmpresaSerializer,
    EmpresaListSerializer,
    ProductoCreateSerializer,
    ProductoSerializer,
    ProductoListSerializer,
    CrearProductoResponseSerializer,
    InventarioSerializer,
    MovimientoCreateSerializer,
    RegistrarMovimientoResponseSerializer,
)

# Importar casos de uso
from aplicacion.casos_uso.crear_producto import CrearProductoCasoDeUso
from aplicacion.casos_uso.registrar_movimiento import RegistrarMovimientoCasoDeUso

# Importar repositorios
from infraestructura.django_orm.repositorio_empresa import RepositorioEmpresaDjango
from infraestructura.django_orm.repositorio_producto import RepositorioProductoDjango
from infraestructura.django_orm.repositorios import (
    RepositorioInventarioDjango,
    RepositorioMovimientoDjango,
    RepositorioUsuarioDjango
)

# Importar entidades del dominio
from dominio.entidades.empresa import Empresa
from dominio.excepciones.excepciones_negocio import (
    EmpresaNoEncontrada,
    ProductoNoEncontrado,
    NITDuplicado,
    DatosInvalidos,
    ExcepcionDominio
)


# ==================== EMPRESAS ====================

class EmpresaListCreateView(APIView):
    """
    GET: Lista todas las empresas
    POST: Crea una nueva empresa
    """
    permission_classes = [AllowAny]  # Cambiar a IsAuthenticated en producción
    
    def get(self, request):
        """Listar todas las empresas"""
        try:
            repo_empresa = RepositorioEmpresaDjango()
            empresas = repo_empresa.listar_todas()
            
            # Convertir entidades a diccionarios
            empresas_data = [empresa.to_dict() for empresa in empresas]
            
            serializer = EmpresaListSerializer(empresas_data, many=True)
            
            return Response({
                'count': len(empresas_data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al listar empresas',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Crear una nueva empresa"""
        serializer = EmpresaSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear entidad del dominio
            empresa = Empresa(
                nombre=serializer.validated_data['nombre'],
                nit=serializer.validated_data['nit'],
                direccion=serializer.validated_data['direccion'],
                telefono=serializer.validated_data['telefono'],
                email=serializer.validated_data['email']
            )
            
            # Persistir usando repositorio
            repo_empresa = RepositorioEmpresaDjango()
            
            # Verificar que el NIT no exista
            if repo_empresa.existe_nit(empresa.nit):
                raise NITDuplicado(f"El NIT {empresa.nit} ya está registrado")
            
            empresa_guardada = repo_empresa.guardar(empresa)
            
            # Devolver respuesta
            response_serializer = EmpresaSerializer(empresa_guardada.to_dict())
            
            return Response({
                'mensaje': 'Empresa creada exitosamente',
                'empresa': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except NITDuplicado as e:
            return Response({
                'error': 'NIT duplicado',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except DatosInvalidos as e:
            return Response({
                'error': 'Datos inválidos',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'error': 'Error al crear empresa',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmpresaDetailView(APIView):
    """
    GET: Obtiene una empresa por ID
    """
    permission_classes = [AllowAny]
    
    def get(self, request, empresa_id):
        """Obtener empresa por ID"""
        try:
            repo_empresa = RepositorioEmpresaDjango()
            empresa = repo_empresa.obtener_por_id(empresa_id)
            
            if not empresa:
                raise EmpresaNoEncontrada(f"Empresa con ID {empresa_id} no encontrada")
            
            serializer = EmpresaSerializer(empresa.to_dict())
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except EmpresaNoEncontrada as e:
            return Response({
                'error': 'Empresa no encontrada',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


# ==================== PRODUCTOS ====================

class ProductoListCreateView(APIView):
    """
    GET: Lista todos los productos
    POST: Crea un nuevo producto usando el caso de uso
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Listar productos"""
        try:
            repo_producto = RepositorioProductoDjango()
            empresa_id = request.query_params.get('empresa_id')
            
            if empresa_id:
                productos = repo_producto.listar_por_empresa(int(empresa_id))
            else:
                # Listar todos (implementar método en repositorio si no existe)
                from infraestructura.django_orm.models import ProductoModel
                productos_models = ProductoModel.objects.all()
                productos = [repo_producto._modelo_a_entidad(p) for p in productos_models]
            
            productos_data = [producto.to_dict() for producto in productos]
            serializer = ProductoListSerializer(productos_data, many=True)
            
            return Response({
                'count': len(productos_data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al listar productos',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Crear producto usando el caso de uso"""
        serializer = ProductoCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Instanciar repositorios
            repo_producto = RepositorioProductoDjango()
            repo_empresa = RepositorioEmpresaDjango()
            repo_inventario = RepositorioInventarioDjango()
            
            # Instanciar caso de uso
            caso_uso = CrearProductoCasoDeUso(
                repositorio_producto=repo_producto,
                repositorio_empresa=repo_empresa,
                repositorio_inventario=repo_inventario
            )
            
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(serializer.validated_data)
            
            # Serializar respuesta
            response_serializer = CrearProductoResponseSerializer(resultado)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except EmpresaNoEncontrada as e:
            return Response({
                'error': 'Empresa no encontrada',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
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
                'error': 'Error al crear producto',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductoDetailView(APIView):
    """
    GET: Obtiene un producto por ID
    """
    permission_classes = [AllowAny]
    
    def get(self, request, producto_id):
        """Obtener producto por ID"""
        try:
            repo_producto = RepositorioProductoDjango()
            producto = repo_producto.obtener_por_id(producto_id)
            
            if not producto:
                raise ProductoNoEncontrado(f"Producto con ID {producto_id} no encontrado")
            
            serializer = ProductoSerializer(producto.to_dict())
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ProductoNoEncontrado as e:
            return Response({
                'error': 'Producto no encontrado',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)


# ==================== INVENTARIO ====================

class InventarioListView(APIView):
    """
    GET: Lista inventarios
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Listar inventarios"""
        try:
            repo_inventario = RepositorioInventarioDjango()
            empresa_id = request.query_params.get('empresa_id')
            
            if empresa_id:
                inventarios = repo_inventario.listar_por_empresa(int(empresa_id))
            else:
                # Listar todos
                from infraestructura.django_orm.models import InventarioModel
                inventarios_models = InventarioModel.objects.all()
                inventarios = [repo_inventario._modelo_a_entidad(i) for i in inventarios_models]
            
            inventarios_data = []
            for inv in inventarios:
                inv_dict = inv.to_dict()
                inv_dict['estado_stock'] = inv.obtener_estado_stock()
                inventarios_data.append(inv_dict)
            
            serializer = InventarioSerializer(inventarios_data, many=True)
            
            return Response({
                'count': len(inventarios_data),
                'results': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error al listar inventarios',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== MOVIMIENTOS ====================

class MovimientoCreateView(APIView):
    """
    POST: Registra un movimiento de inventario usando el caso de uso
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Registrar movimiento"""
        serializer = MovimientoCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Instanciar repositorios
            repo_producto = RepositorioProductoDjango()
            repo_inventario = RepositorioInventarioDjango()
            repo_movimiento = RepositorioMovimientoDjango()
            repo_usuario = RepositorioUsuarioDjango()
            
            # Instanciar caso de uso
            caso_uso = RegistrarMovimientoCasoDeUso(
                repositorio_producto=repo_producto,
                repositorio_inventario=repo_inventario,
                repositorio_movimiento=repo_movimiento,
                repositorio_usuario=repo_usuario
            )
            
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(serializer.validated_data)
            
            # Serializar respuesta
            response_serializer = RegistrarMovimientoResponseSerializer(resultado)
            
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
            
        except ProductoNoEncontrado as e:
            return Response({
                'error': 'Producto no encontrado',
                'detalle': str(e)
            }, status=status.HTTP_404_NOT_FOUND)
        
        except ExcepcionDominio as e:
            return Response({
                'error': 'Error de negocio',
                'detalle': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'error': 'Error al registrar movimiento',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
