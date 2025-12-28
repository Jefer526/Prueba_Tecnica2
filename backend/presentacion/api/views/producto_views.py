"""
Vistas de Producto - Capa de Presentación
Usa casos de uso del dominio
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from aplicacion.casos_uso.crear_producto import CrearProductoCasoDeUso
from infraestructura.django_orm.repositorio_producto import RepositorioProductoDjango
from infraestructura.django_orm.repositorio_empresa import RepositorioEmpresaDjango
from infraestructura.django_orm.repositorio_inventario import RepositorioInventarioDjango
from dominio.excepciones.excepciones_negocio import ExcepcionDominio


class CrearProductoView(APIView):
    """
    Vista para crear un producto
    Delega toda la lógica al caso de uso
    """
    
    def post(self, request):
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
        
        try:
            # Ejecutar caso de uso
            resultado = caso_uso.ejecutar(request.data)
            
            return Response(
                resultado,
                status=status.HTTP_201_CREATED
            )
            
        except ExcepcionDominio as e:
            return Response(
                {
                    'error': e.codigo_error,
                    'mensaje': e.mensaje
                },
                status=status.HTTP_400_BAD_REQUEST
            )