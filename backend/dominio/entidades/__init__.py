"""
Entidades del Dominio
Modelos del negocio en Python puro
"""

from .empresa import Empresa
from .producto import Producto, CategoriaProducto, obtener_prefijo_categoria
from .inventario import RegistroInventario, EstadoStock
from .movimiento import MovimientoInventario, TipoMovimiento
from .usuario import Usuario, RolUsuario

__all__ = [
    "Empresa",
    "Producto",
    "CategoriaProducto",
    "obtener_prefijo_categoria",
    "RegistroInventario",
    "EstadoStock",
    "MovimientoInventario",
    "TipoMovimiento",
    "Usuario",
    "RolUsuario",
]
