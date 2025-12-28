"""
Entidad Producto - Capa de Dominio
Entidad pura sin dependencias de Django, REST o infraestructura
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from enum import Enum


class CategoriaProducto(Enum):
    """Categorías disponibles para productos"""
    TECNOLOGIA = "TECNOLOGIA"
    OFICINA = "OFICINA"
    CONSUMIBLES = "CONSUMIBLES"
    EQUIPAMIENTO = "EQUIPAMIENTO"
    OTROS = "OTROS"


@dataclass
class Producto:
    """
    Entidad de dominio que representa un Producto
    Reglas de negocio:
    - El código debe ser único y generarse automáticamente
    - Los precios deben ser positivos
    - El stock mínimo debe ser menor que el stock máximo
    - Los precios en diferentes monedas se calculan automáticamente
    """
    nombre: str
    descripcion: str
    precio_usd: Decimal
    categoria: CategoriaProducto
    empresa_id: int
    id: Optional[int] = None
    codigo: Optional[str] = None
    precio_cop: Optional[Decimal] = None
    precio_eur: Optional[Decimal] = None
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None
    
    # Tasas de cambio (podrían venir de un servicio externo)
    TASA_USD_A_COP: Decimal = Decimal('4200')
    TASA_USD_A_EUR: Decimal = Decimal('0.92')
    
    def __post_init__(self):
        """Validaciones y cálculos automáticos al crear la entidad"""
        self.validar()
        self.calcular_precios_otras_monedas()
    
    def validar(self) -> None:
        """
        Valida las reglas de negocio de la entidad Producto
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre del producto es obligatorio")
        
        if len(self.nombre) < 3:
            raise ValueError("El nombre del producto debe tener al menos 3 caracteres")
        
        if not self.descripcion or len(self.descripcion.strip()) == 0:
            raise ValueError("La descripción del producto es obligatoria")
        
        if self.precio_usd <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        
        if not isinstance(self.categoria, CategoriaProducto):
            raise ValueError(f"Categoría inválida. Debe ser una de: {[c.value for c in CategoriaProducto]}")
        
        if self.empresa_id is None or self.empresa_id <= 0:
            raise ValueError("El producto debe estar asociado a una empresa válida")
    
    def calcular_precios_otras_monedas(self) -> None:
        """
        Calcula automáticamente los precios en COP y EUR basados en USD
        Esta es una regla de negocio del dominio
        """
        self.precio_cop = self.precio_usd * self.TASA_USD_A_COP
        self.precio_eur = self.precio_usd * self.TASA_USD_A_EUR
    
    def generar_codigo(self, prefijo: str, numero_secuencial: int) -> str:
        """
        Genera el código del producto
        Formato: PP#### donde PP es el prefijo de 2 letras y #### es el número
        Ejemplo: PO0001, TE0042
        """
        if not prefijo or len(prefijo) != 2:
            raise ValueError("El prefijo debe tener exactamente 2 caracteres")
        
        codigo = f"{prefijo.upper()}{numero_secuencial:04d}"
        self.codigo = codigo
        return codigo
    
    def actualizar_precio(self, nuevo_precio_usd: Decimal) -> None:
        """
        Actualiza el precio del producto y recalcula otras monedas
        Regla de negocio: Los precios siempre se sincronizan
        """
        if nuevo_precio_usd <= 0:
            raise ValueError("El precio debe ser mayor a cero")
        
        self.precio_usd = nuevo_precio_usd
        self.calcular_precios_otras_monedas()
        self.fecha_actualizacion = datetime.now()
    
    def actualizar_informacion(
        self,
        nombre: Optional[str] = None,
        descripcion: Optional[str] = None,
        categoria: Optional[CategoriaProducto] = None
    ) -> None:
        """
        Actualiza la información básica del producto
        Solo actualiza los campos proporcionados
        """
        if nombre:
            self.nombre = nombre
        if descripcion:
            self.descripcion = descripcion
        if categoria:
            self.categoria = categoria
        
        self.fecha_actualizacion = datetime.now()
        self.validar()
    
    def activar(self) -> None:
        """Activa el producto"""
        self.activo = True
        self.fecha_actualizacion = datetime.now()
    
    def desactivar(self) -> None:
        """Desactiva el producto (soft delete)"""
        self.activo = False
        self.fecha_actualizacion = datetime.now()
    
    def es_activo(self) -> bool:
        """Verifica si el producto está activo"""
        return self.activo
    
    def obtener_precio_en_moneda(self, moneda: str) -> Decimal:
        """
        Obtiene el precio del producto en la moneda especificada
        """
        moneda = moneda.upper()
        if moneda == 'USD':
            return self.precio_usd
        elif moneda == 'COP':
            return self.precio_cop
        elif moneda == 'EUR':
            return self.precio_eur
        else:
            raise ValueError(f"Moneda no soportada: {moneda}")
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario para persistencia"""
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio_usd': float(self.precio_usd),
            'precio_cop': float(self.precio_cop) if self.precio_cop else None,
            'precio_eur': float(self.precio_eur) if self.precio_eur else None,
            'categoria': self.categoria.value,
            'empresa_id': self.empresa_id,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Producto':
        """Crea una entidad desde un diccionario"""
        return cls(
            id=data.get('id'),
            codigo=data.get('codigo'),
            nombre=data['nombre'],
            descripcion=data['descripcion'],
            precio_usd=Decimal(str(data['precio_usd'])),
            precio_cop=Decimal(str(data['precio_cop'])) if data.get('precio_cop') else None,
            precio_eur=Decimal(str(data['precio_eur'])) if data.get('precio_eur') else None,
            categoria=CategoriaProducto(data['categoria']),
            empresa_id=data['empresa_id'],
            activo=data.get('activo', True),
            fecha_creacion=datetime.fromisoformat(data['fecha_creacion']) if data.get('fecha_creacion') else datetime.now(),
            fecha_actualizacion=datetime.fromisoformat(data['fecha_actualizacion']) if data.get('fecha_actualizacion') else None
        )
    
    def __str__(self) -> str:
        return f"Producto({self.codigo} - {self.nombre})"
    
    def __repr__(self) -> str:
        return f"Producto(id={self.id}, codigo='{self.codigo}', nombre='{self.nombre}', precio_usd={self.precio_usd})"
