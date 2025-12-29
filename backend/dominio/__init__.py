"""
Lite Thinking - Capa de Dominio
Sistema de Gestión de Inventario

Este paquete contiene las entidades y reglas de negocio puras,
sin dependencias de frameworks como Django o FastAPI.

Arquitectura: Clean Architecture - Capa de Dominio
"""

__version__ = "1.0.0"
__author__ = "Jeffer Niño"

# Importar todas las entidades
from .entidades.empresa import Empresa
from .entidades.producto import Producto, CategoriaProducto, obtener_prefijo_categoria
from .entidades.inventario import RegistroInventario, EstadoStock
from .entidades.movimiento import MovimientoInventario, TipoMovimiento
from .entidades.usuario import Usuario, RolUsuario

# Importar todas las excepciones
from .excepciones.excepciones_negocio import (
    # Base
    ExcepcionDominio,
    
    # Producto
    ProductoNoEncontrado,
    ProductoInactivo,
    CodigoProductoDuplicado,
    PrecioInvalido,
    CategoriaInvalida,
    
    # Inventario
    StockInsuficiente,
    StockNegativo,
    StockMaximoExcedido,
    InventarioNoEncontrado,
    
    # Empresa
    NITDuplicado,
    NITInvalido,
    EmpresaNoEncontrada,
    EmpresaInactiva,
    
    # Usuario
    UsuarioNoEncontrado,
    EmailDuplicado,
    CredencialesInvalidas,
    
    # General
    DatosInvalidos,
)

# Exportar todo
__all__ = [
    # Versión
    "__version__",
    "__author__",
    
    # Entidades
    "Empresa",
    "Producto",
    "CategoriaProducto",
    "RegistroInventario",
    "EstadoStock",
    "MovimientoInventario",
    "TipoMovimiento",
    "Usuario",
    "RolUsuario",
    
    # Funciones auxiliares
    "obtener_prefijo_categoria",
    
    # Excepciones Base
    "ExcepcionDominio",
    
    # Excepciones Producto
    "ProductoNoEncontrado",
    "ProductoInactivo",
    "CodigoProductoDuplicado",
    "PrecioInvalido",
    "CategoriaInvalida",
    
    # Excepciones Inventario
    "StockInsuficiente",
    "StockNegativo",
    "StockMaximoExcedido",
    "InventarioNoEncontrado",
    
    # Excepciones Empresa
    "NITDuplicado",
    "NITInvalido",
    "EmpresaNoEncontrada",
    "EmpresaInactiva",
    
    # Excepciones Usuario
    "UsuarioNoEncontrado",
    "EmailDuplicado",
    "CredencialesInvalidas",
    
    # Excepciones General
    "DatosInvalidos",
]
