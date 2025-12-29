"""
Entidad Inventario - Capa de Dominio
Entidad pura sin dependencias de Django, REST o infraestructura
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class RegistroInventario:
    """
    Entidad de dominio que representa el inventario de un producto
    Reglas de negocio:
    - El stock nunca puede ser negativo
    - Debe alertar cuando el stock esté por debajo del mínimo
    - El stock máximo debe ser mayor que el mínimo
    """
    producto_id: int
    stock_actual: int
    stock_minimo: int
    stock_maximo: int
    empresa_id: int
    id: Optional[int] = None
    requiere_reorden: bool = False
    ultima_actualizacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones y cálculos automáticos al crear la entidad"""
        self.validar()
        self.evaluar_necesidad_reorden()
    
    def validar(self) -> None:
        """
        Valida las reglas de negocio de la entidad Inventario
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if self.stock_actual < 0:
            raise ValueError("El stock actual no puede ser negativo")
        
        if self.stock_minimo < 0:
            raise ValueError("El stock mínimo no puede ser negativo")
        
        if self.stock_maximo < 0:
            raise ValueError("El stock máximo no puede ser negativo")
        
        if self.stock_minimo >= self.stock_maximo:
            raise ValueError("El stock mínimo debe ser menor que el stock máximo")
        
        if self.producto_id is None or self.producto_id <= 0:
            raise ValueError("El inventario debe estar asociado a un producto válido")
        
        if self.empresa_id is None or self.empresa_id <= 0:
            raise ValueError("El inventario debe estar asociado a una empresa válida")
    
    def evaluar_necesidad_reorden(self) -> bool:
        """
        Evalúa si el inventario requiere reorden
        Regla de negocio: Se requiere reorden cuando stock_actual <= stock_minimo
        """
        self.requiere_reorden = self.stock_actual <= self.stock_minimo
        return self.requiere_reorden
    
    def tiene_stock_suficiente(self, cantidad: int) -> bool:
        """
        Verifica si hay stock suficiente para una salida
        """
        return self.stock_actual >= cantidad
    
    def puede_recibir_entrada(self, cantidad: int) -> bool:
        """
        Verifica si se puede recibir una entrada sin exceder el stock máximo
        Regla de negocio: No permitir que el stock exceda el máximo
        """
        stock_resultante = self.stock_actual + cantidad
        return stock_resultante <= self.stock_maximo
    
    def registrar_entrada(self, cantidad: int) -> None:
        """
        Registra una entrada de inventario
        Regla de negocio: Incrementa el stock actual
        """
        if cantidad <= 0:
            raise ValueError("La cantidad de entrada debe ser positiva")
        
        if not self.puede_recibir_entrada(cantidad):
            raise ValueError(
                f"La entrada de {cantidad} unidades excedería el stock máximo ({self.stock_maximo}). "
                f"Stock actual: {self.stock_actual}"
            )
        
        self.stock_actual += cantidad
        self.ultima_actualizacion = datetime.now()
        self.evaluar_necesidad_reorden()
    
    def registrar_salida(self, cantidad: int) -> None:
        """
        Registra una salida de inventario
        Regla de negocio: Decrementa el stock actual
        """
        if cantidad <= 0:
            raise ValueError("La cantidad de salida debe ser positiva")
        
        if not self.tiene_stock_suficiente(cantidad):
            raise ValueError(
                f"Stock insuficiente. Solicitado: {cantidad}, Disponible: {self.stock_actual}"
            )
        
        self.stock_actual -= cantidad
        self.ultima_actualizacion = datetime.now()
        self.evaluar_necesidad_reorden()
    
    def ajustar_stock(self, nuevo_stock: int) -> None:
        """
        Ajusta el stock a un valor específico (para correcciones)
        Regla de negocio: Usado en ajustes por inventario físico
        """
        if nuevo_stock < 0:
            raise ValueError("El stock no puede ser negativo")
        
        if nuevo_stock > self.stock_maximo:
            raise ValueError(
                f"El ajuste de stock ({nuevo_stock}) excedería el stock máximo ({self.stock_maximo})"
            )
        
        self.stock_actual = nuevo_stock
        self.ultima_actualizacion = datetime.now()
        self.evaluar_necesidad_reorden()
    
    def actualizar_limites(self, stock_minimo: Optional[int] = None, stock_maximo: Optional[int] = None) -> None:
        """
        Actualiza los límites de stock
        """
        if stock_minimo is not None:
            if stock_minimo < 0:
                raise ValueError("El stock mínimo no puede ser negativo")
            self.stock_minimo = stock_minimo
        
        if stock_maximo is not None:
            if stock_maximo < 0:
                raise ValueError("El stock máximo no puede ser negativo")
            self.stock_maximo = stock_maximo
        
        # Validar que mínimo < máximo
        if self.stock_minimo >= self.stock_maximo:
            raise ValueError("El stock mínimo debe ser menor que el stock máximo")
        
        self.ultima_actualizacion = datetime.now()
        self.evaluar_necesidad_reorden()
    
    def obtener_porcentaje_stock(self) -> Decimal:
        """
        Calcula el porcentaje de stock actual respecto al máximo
        """
        if self.stock_maximo == 0:
            return Decimal('0')
        
        porcentaje = (Decimal(self.stock_actual) / Decimal(self.stock_maximo)) * Decimal('100')
        return porcentaje.quantize(Decimal('0.01'))
    
    def obtener_estado_stock(self) -> str:
        """
        Obtiene el estado del stock según el porcentaje
        Reglas de negocio:
        - CRITICO: <= stock_minimo
        - BAJO: > stock_minimo y <= 50% del máximo
        - NORMAL: > 50% y <= 80% del máximo
        - ALTO: > 80% del máximo
        """
        if self.stock_actual <= self.stock_minimo:
            return "CRITICO"
        
        porcentaje = float(self.obtener_porcentaje_stock())
        
        if porcentaje <= 50:
            return "BAJO"
        elif porcentaje <= 80:
            return "NORMAL"
        else:
            return "ALTO"
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'empresa_id': self.empresa_id,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'requiere_reorden': self.requiere_reorden,
            'ultima_actualizacion': self.ultima_actualizacion,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RegistroInventario':
        """Crea una entidad desde un diccionario"""
        return cls(
            id=data.get('id'),
            producto_id=data['producto_id'],
            empresa_id=data['empresa_id'],
            stock_actual=data['stock_actual'],
            stock_minimo=data['stock_minimo'],
            stock_maximo=data['stock_maximo'],
            requiere_reorden=data.get('requiere_reorden', False),
            ultima_actualizacion=datetime.fromisoformat(data['ultima_actualizacion']) if data.get('ultima_actualizacion') else datetime.now()
        )
    
    def __str__(self) -> str:
        return f"Inventario(Producto {self.producto_id}: {self.stock_actual}/{self.stock_maximo})"
    
    def __repr__(self) -> str:
        return (
            f"RegistroInventario(id={self.id}, producto_id={self.producto_id}, "
            f"stock_actual={self.stock_actual}, requiere_reorden={self.requiere_reorden})"
        )
