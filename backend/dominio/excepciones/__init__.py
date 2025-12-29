"""
Excepciones del Dominio
Excepciones específicas de reglas de negocio
"""

from .excepciones_negocio import (
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

__all__ = [
    # Base
    "ExcepcionDominio",
    
    # Producto
    "ProductoNoEncontrado",
    "ProductoInactivo",
    "CodigoProductoDuplicado",
    "PrecioInvalido",
    "CategoriaInvalida",
    
    # Inventario
    "StockInsuficiente",
    "StockNegativo",
    "StockMaximoExcedido",
    "InventarioNoEncontrado",
    
    # Empresa
    "NITDuplicado",
    "NITInvalido",
    "EmpresaNoEncontrada",
    "EmpresaInactiva",
    
    # Usuario
    "UsuarioNoEncontrado",
    "EmailDuplicado",
    "CredencialesInvalidas",
    
    # General
    "DatosInvalidos",
]
