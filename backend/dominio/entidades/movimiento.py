"""
Entidad MovimientoInventario - Capa de Dominio
Entidad pura sin dependencias de Django, REST o infraestructura
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoMovimiento(Enum):
    """Tipos de movimientos de inventario"""
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"
    DEVOLUCION = "DEVOLUCION"
    TRANSFERENCIA = "TRANSFERENCIA"


@dataclass
class MovimientoInventario:
    """
    Entidad de dominio que representa un movimiento de inventario
    Reglas de negocio:
    - Todo movimiento debe tener un tipo válido
    - Las cantidades deben ser positivas
    - Los movimientos son inmutables una vez creados
    - Debe registrar quién realizó el movimiento
    """
    tipo_movimiento: TipoMovimiento
    producto_id: int
    cantidad: int
    empresa_id: int
    usuario_id: int
    observaciones: str = ""
    id: Optional[int] = None
    fecha_movimiento: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones automáticas al crear la entidad"""
        self.validar()
    
    def validar(self) -> None:
        """
        Valida las reglas de negocio de la entidad MovimientoInventario
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not isinstance(self.tipo_movimiento, TipoMovimiento):
            raise ValueError(
                f"Tipo de movimiento inválido. Debe ser uno de: {[t.value for t in TipoMovimiento]}"
            )
        
        if self.cantidad <= 0:
            raise ValueError("La cantidad del movimiento debe ser positiva")
        
        if self.producto_id is None or self.producto_id <= 0:
            raise ValueError("El movimiento debe estar asociado a un producto válido")
        
        if self.empresa_id is None or self.empresa_id <= 0:
            raise ValueError("El movimiento debe estar asociado a una empresa válida")
        
        if self.usuario_id is None or self.usuario_id <= 0:
            raise ValueError("El movimiento debe tener un usuario responsable")
    
    def es_entrada(self) -> bool:
        """Verifica si el movimiento incrementa el stock"""
        return self.tipo_movimiento in [TipoMovimiento.ENTRADA, TipoMovimiento.DEVOLUCION]
    
    def es_salida(self) -> bool:
        """Verifica si el movimiento decrementa el stock"""
        return self.tipo_movimiento in [TipoMovimiento.SALIDA, TipoMovimiento.TRANSFERENCIA]
    
    def es_ajuste(self) -> bool:
        """Verifica si el movimiento es un ajuste de inventario"""
        return self.tipo_movimiento == TipoMovimiento.AJUSTE
    
    def obtener_impacto_stock(self) -> int:
        """
        Obtiene el impacto del movimiento en el stock
        Retorna:
            int: Cantidad positiva para entradas, negativa para salidas
        """
        if self.es_entrada():
            return self.cantidad
        elif self.es_salida():
            return -self.cantidad
        else:  # AJUSTE
            # Los ajustes se manejan directamente, no como delta
            return 0
    
    def agregar_observacion(self, observacion: str) -> None:
        """
        Agrega o actualiza las observaciones del movimiento
        Nota: Esto solo es permitido antes de persistir
        """
        if observacion and len(observacion.strip()) > 0:
            self.observaciones = observacion.strip()
    
    def obtener_descripcion(self) -> str:
        """
        Obtiene una descripción legible del movimiento
        """
        tipo_str = self.tipo_movimiento.value
        return f"{tipo_str} de {self.cantidad} unidades"
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'nit': self.nit,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
            'fecha_actualizacion': self.fecha_actualizacion,
        }
    @classmethod
    def from_dict(cls, data: dict) -> 'MovimientoInventario':
        """Crea una entidad desde un diccionario"""
        return cls(
            id=data.get('id'),
            tipo_movimiento=TipoMovimiento(data['tipo_movimiento']),
            producto_id=data['producto_id'],
            cantidad=data['cantidad'],
            empresa_id=data['empresa_id'],
            usuario_id=data['usuario_id'],
            observaciones=data.get('observaciones', ''),
            fecha_movimiento=datetime.fromisoformat(data['fecha_movimiento']) if data.get('fecha_movimiento') else datetime.now()
        )
    
    def __str__(self) -> str:
        return f"Movimiento({self.tipo_movimiento.value} - {self.cantidad} unidades)"
    
    def __repr__(self) -> str:
        return (
            f"MovimientoInventario(id={self.id}, tipo='{self.tipo_movimiento.value}', "
            f"producto_id={self.producto_id}, cantidad={self.cantidad})"
        )
