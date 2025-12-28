"""
Configuración de Inyección de Dependencias
Centraliza la creación de repositorios y casos de uso
"""
from infraestructura.django_orm.repositorio_producto import RepositorioProductoDjango
from infraestructura.django_orm.repositorio_empresa import RepositorioEmpresaDjango
from infraestructura.django_orm.repositorio_inventario import RepositorioInventarioDjango
from infraestructura.django_orm.repositorio_movimiento import RepositorioMovimientoDjango
from aplicacion.casos_uso.crear_producto import CrearProductoCasoDeUso
from aplicacion.casos_uso.registrar_movimiento import RegistrarMovimientoCasoDeUso


class Contenedor:
    """Contenedor de dependencias"""
    
    # Repositorios (singletons)
    _repo_producto = None
    _repo_empresa = None
    _repo_inventario = None
    _repo_movimiento = None
    
    @classmethod
    def obtener_repo_producto(cls):
        if cls._repo_producto is None:
            cls._repo_producto = RepositorioProductoDjango()
        return cls._repo_producto
    
    @classmethod
    def obtener_repo_empresa(cls):
        if cls._repo_empresa is None:
            cls._repo_empresa = RepositorioEmpresaDjango()
        return cls._repo_empresa
    
    @classmethod
    def obtener_repo_inventario(cls):
        if cls._repo_inventario is None:
            cls._repo_inventario = RepositorioInventarioDjango()
        return cls._repo_inventario
    
    @classmethod
    def obtener_repo_movimiento(cls):
        if cls._repo_movimiento is None:
            cls._repo_movimiento = RepositorioMovimientoDjango()
        return cls._repo_movimiento
    
    # Casos de uso
    @classmethod
    def obtener_crear_producto_caso_uso(cls):
        return CrearProductoCasoDeUso(
            repositorio_producto=cls.obtener_repo_producto(),
            repositorio_empresa=cls.obtener_repo_empresa(),
            repositorio_inventario=cls.obtener_repo_inventario()
        )
    
    @classmethod
    def obtener_registrar_movimiento_caso_uso(cls):
        return RegistrarMovimientoCasoDeUso(
            repositorio_producto=cls.obtener_repo_producto(),
            repositorio_inventario=cls.obtener_repo_inventario(),
            repositorio_movimiento=cls.obtener_repo_movimiento()
        )