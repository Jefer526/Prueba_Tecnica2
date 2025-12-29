"""
Interfaces de Repositorios - Capa de Aplicación
Contratos que define cómo deben implementarse los repositorios
Sin dependencias de Django o implementación específica
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal


# === REPOSITORIO DE EMPRESA ===

class IRepositorioEmpresa(ABC):
    """
    Interfaz que define el contrato para el repositorio de Empresa
    Implementaciones concretas estarán en la capa de infraestructura
    """
    
    @abstractmethod
    def guardar(self, empresa) -> 'Empresa':
        """
        Persiste una empresa en el almacenamiento
        Retorna: La empresa con su ID asignado
        """
        pass
    
    @abstractmethod
    def obtener_por_id(self, empresa_id: int) -> Optional['Empresa']:
        """
        Obtiene una empresa por su ID
        Retorna: La empresa o None si no existe
        """
        pass
    
    @abstractmethod
    def obtener_por_nit(self, nit: str) -> Optional['Empresa']:
        """
        Obtiene una empresa por su NIT
        Retorna: La empresa o None si no existe
        """
        pass
    
    @abstractmethod
    def listar_activas(self) -> List['Empresa']:
        """
        Lista todas las empresas activas
        Retorna: Lista de empresas activas
        """
        pass
    
    @abstractmethod
    def listar_todas(self) -> List['Empresa']:
        """
        Lista todas las empresas (activas e inactivas)
        Retorna: Lista de todas las empresas
        """
        pass
    
    @abstractmethod
    def existe_nit(self, nit: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe una empresa con el NIT dado
        Args:
            nit: NIT a verificar
            excluir_id: ID de empresa a excluir de la búsqueda (para actualizaciones)
        Retorna: True si existe, False si no
        """
        pass
    
    @abstractmethod
    def actualizar(self, empresa) -> 'Empresa':
        """
        Actualiza una empresa existente
        Retorna: La empresa actualizada
        """
        pass
    
    @abstractmethod
    def eliminar(self, empresa_id: int) -> bool:
        """
        Elimina (soft delete) una empresa
        Retorna: True si se eliminó, False si no
        """
        pass


# === REPOSITORIO DE PRODUCTO ===

class IRepositorioProducto(ABC):
    """
    Interfaz que define el contrato para el repositorio de Producto
    """
    
    @abstractmethod
    def guardar(self, producto) -> 'Producto':
        """
        Persiste un producto en el almacenamiento
        Retorna: El producto con su ID asignado
        """
        pass
    
    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Optional['Producto']:
        """
        Obtiene un producto por su ID
        Retorna: El producto o None si no existe
        """
        pass
    
    @abstractmethod
    def obtener_por_codigo(self, codigo: str) -> Optional['Producto']:
        """
        Obtiene un producto por su código
        Retorna: El producto o None si no existe
        """
        pass
    
    @abstractmethod
    def listar_por_empresa(self, empresa_id: int, solo_activos: bool = True) -> List['Producto']:
        """
        Lista productos de una empresa
        Args:
            empresa_id: ID de la empresa
            solo_activos: Si es True, solo retorna productos activos
        Retorna: Lista de productos
        """
        pass
    
    @abstractmethod
    def listar_por_categoria(self, categoria: str, solo_activos: bool = True) -> List['Producto']:
        """
        Lista productos de una categoría
        Args:
            categoria: Categoría a filtrar
            solo_activos: Si es True, solo retorna productos activos
        Retorna: Lista de productos
        """
        pass
    
    @abstractmethod
    def buscar_por_nombre(self, termino: str, empresa_id: Optional[int] = None) -> List['Producto']:
        """
        Busca productos por nombre
        Args:
            termino: Término de búsqueda
            empresa_id: Opcional, filtrar por empresa
        Retorna: Lista de productos que coinciden
        """
        pass
    
    @abstractmethod
    def existe_codigo(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica si ya existe un producto con el código dado
        """
        pass
    
    @abstractmethod
    def obtener_siguiente_numero_codigo(self, prefijo: str) -> int:
        """
        Obtiene el siguiente número secuencial para un prefijo de código
        Args:
            prefijo: Prefijo de 2 letras (ej: "PO", "TE")
        Retorna: Siguiente número disponible
        """
        pass
    
    @abstractmethod
    def actualizar(self, producto) -> 'Producto':
        """
        Actualiza un producto existente
        Retorna: El producto actualizado
        """
        pass
    
    @abstractmethod
    def eliminar(self, producto_id: int) -> bool:
        """
        Elimina (soft delete) un producto
        Retorna: True si se eliminó, False si no
        """
        pass


# === REPOSITORIO DE INVENTARIO ===

class IRepositorioInventario(ABC):
    """
    Interfaz que define el contrato para el repositorio de Inventario
    """
    
    @abstractmethod
    def guardar(self, inventario) -> 'RegistroInventario':
        """
        Persiste un registro de inventario
        Retorna: El inventario con su ID asignado
        """
        pass
    
    @abstractmethod
    def obtener_por_id(self, inventario_id: int) -> Optional['RegistroInventario']:
        """
        Obtiene un registro de inventario por su ID
        """
        pass
    
    @abstractmethod
    def obtener_por_producto(self, producto_id: int) -> Optional['RegistroInventario']:
        """
        Obtiene el registro de inventario de un producto
        Retorna: El inventario o None si no existe
        """
        pass
    
    @abstractmethod
    def listar_por_empresa(self, empresa_id: int) -> List['RegistroInventario']:
        """
        Lista todos los inventarios de una empresa
        """
        pass
    
    @abstractmethod
    def listar_con_stock_bajo(self, empresa_id: Optional[int] = None) -> List['RegistroInventario']:
        """
        Lista inventarios que requieren reorden (stock bajo)
        Args:
            empresa_id: Opcional, filtrar por empresa
        Retorna: Lista de inventarios con stock bajo
        """
        pass
    
    @abstractmethod
    def listar_por_estado(self, estado: str, empresa_id: Optional[int] = None) -> List['RegistroInventario']:
        """
        Lista inventarios por estado (CRITICO, BAJO, NORMAL, ALTO)
        """
        pass
    
    @abstractmethod
    def actualizar(self, inventario) -> 'RegistroInventario':
        """
        Actualiza un registro de inventario
        Retorna: El inventario actualizado
        """
        pass
    
    @abstractmethod
    def existe_inventario(self, producto_id: int) -> bool:
        """
        Verifica si existe registro de inventario para un producto
        """
        pass


# === REPOSITORIO DE MOVIMIENTO ===

class IRepositorioMovimiento(ABC):
    """
    Interfaz que define el contrato para el repositorio de Movimiento
    """
    
    @abstractmethod
    def guardar(self, movimiento) -> 'MovimientoInventario':
        """
        Persiste un movimiento de inventario
        Retorna: El movimiento con su ID asignado
        """
        pass
    
    @abstractmethod
    def obtener_por_id(self, movimiento_id: int) -> Optional['MovimientoInventario']:
        """
        Obtiene un movimiento por su ID
        """
        pass
    
    @abstractmethod
    def listar_por_producto(
        self, 
        producto_id: int, 
        limite: Optional[int] = None
    ) -> List['MovimientoInventario']:
        """
        Lista movimientos de un producto
        Args:
            producto_id: ID del producto
            limite: Número máximo de registros a retornar
        Retorna: Lista de movimientos ordenados por fecha descendente
        """
        pass
    
    @abstractmethod
    def listar_por_empresa(
        self, 
        empresa_id: int,
        tipo_movimiento: Optional[str] = None,
        fecha_desde: Optional['datetime'] = None,
        fecha_hasta: Optional['datetime'] = None
    ) -> List['MovimientoInventario']:
        """
        Lista movimientos de una empresa con filtros opcionales
        """
        pass
    
    @abstractmethod
    def listar_por_tipo(self, tipo_movimiento: str, empresa_id: Optional[int] = None) -> List['MovimientoInventario']:
        """
        Lista movimientos por tipo
        """
        pass
    
    @abstractmethod
    def contar_por_producto(self, producto_id: int) -> int:
        """
        Cuenta el número de movimientos de un producto
        """
        pass


# === REPOSITORIO DE USUARIO ===

class IRepositorioUsuario(ABC):
    """Interfaz para el repositorio de Usuario"""
    
    @abstractmethod
    def guardar(self, usuario) -> any:
        """Guarda un nuevo usuario"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[dict]:
        """Obtiene un usuario por ID"""
        pass
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por email"""
        pass
    
    @abstractmethod
    def verificar_permisos(self, usuario_id: int, permiso: str) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        pass