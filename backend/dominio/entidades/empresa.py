"""
Entidad Empresa - Capa de Dominio
Entidad pura sin dependencias de Django, REST o infraestructura
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class Empresa:
    """
    Entidad de dominio que representa una Empresa
    Reglas de negocio:
    - El nombre es obligatorio y único
    - NIT debe ser válido según formato colombiano
    - Una empresa puede estar activa o inactiva
    """
    nombre: str
    nit: str
    direccion: str
    telefono: str
    email: str
    id: Optional[int] = None
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones automáticas al crear la entidad"""
        self.validar()
    
    def validar(self) -> None:
        """
        Valida las reglas de negocio de la entidad Empresa
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre de la empresa es obligatorio")
        
        if len(self.nombre) < 3:
            raise ValueError("El nombre de la empresa debe tener al menos 3 caracteres")
        
        if not self.nit or len(self.nit.strip()) == 0:
            raise ValueError("El NIT es obligatorio")
        
        if not self._validar_formato_nit(self.nit):
            raise ValueError("El formato del NIT no es válido")
        
        if not self.email or '@' not in self.email:
            raise ValueError("El email no es válido")
        
        if not self.telefono or len(self.telefono) < 7:
            raise ValueError("El teléfono debe tener al menos 7 dígitos")
    
    def _validar_formato_nit(self, nit: str) -> bool:
        """
        Valida el formato del NIT colombiano
        Formato: XXXXXXXXX-X (9 dígitos + guión + dígito verificador)
        """
        # Eliminar espacios y guiones para validación
        nit_limpio = nit.replace('-', '').replace(' ', '')
        
        # Debe tener entre 9 y 10 dígitos
        if not nit_limpio.isdigit() or len(nit_limpio) < 9 or len(nit_limpio) > 10:
            return False
        
        return True
    
    def activar(self) -> None:
        """Activa la empresa"""
        self.activo = True
        self.fecha_actualizacion = datetime.now()
    
    def desactivar(self) -> None:
        """Desactiva la empresa (soft delete)"""
        self.activo = False
        self.fecha_actualizacion = datetime.now()
    
    def actualizar_informacion(
        self,
        nombre: Optional[str] = None,
        direccion: Optional[str] = None,
        telefono: Optional[str] = None,
        email: Optional[str] = None
    ) -> None:
        """
        Actualiza la información de la empresa
        Solo actualiza los campos proporcionados
        """
        if nombre:
            self.nombre = nombre
        if direccion:
            self.direccion = direccion
        if telefono:
            self.telefono = telefono
        if email:
            self.email = email
        
        self.fecha_actualizacion = datetime.now()
        self.validar()
    
    def es_activa(self) -> bool:
        """Verifica si la empresa está activa"""
        return self.activo
    
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
    def from_dict(cls, data: dict) -> 'Empresa':
        """Crea una entidad desde un diccionario"""
        return cls(
            id=data.get('id'),
            nombre=data['nombre'],
            nit=data['nit'],
            direccion=data['direccion'],
            telefono=data['telefono'],
            email=data['email'],
            activo=data.get('activo', True),
            fecha_creacion=datetime.fromisoformat(data['fecha_creacion']) if data.get('fecha_creacion') else datetime.now(),
            fecha_actualizacion=datetime.fromisoformat(data['fecha_actualizacion']) if data.get('fecha_actualizacion') else None
        )
    
    def __str__(self) -> str:
        return f"Empresa({self.nombre} - {self.nit})"
    
    def __repr__(self) -> str:
        return f"Empresa(id={self.id}, nombre='{self.nombre}', nit='{self.nit}', activo={self.activo})"
