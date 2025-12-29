"""
Entidad Usuario - Capa de Dominio
Entidad pura sin dependencias de Django o frameworks
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import hashlib


class RolUsuario(Enum):
    """Roles disponibles en el sistema"""
    ADMINISTRADOR = "ADMINISTRADOR"
    EXTERNO = "EXTERNO"


@dataclass
class Usuario:
    """
    Entidad de dominio que representa un Usuario
    Reglas de negocio:
    - El email debe ser único y válido
    - La contraseña debe cumplir requisitos mínimos
    - Los roles determinan permisos
    - Las contraseñas se almacenan hasheadas
    """
    nombre: str
    email: str
    password: str  # Hasheada
    rol: RolUsuario
    id: Optional[int] = None
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validaciones automáticas al crear la entidad"""
        self.validar()
    
    def validar(self) -> None:
        """
        Valida las reglas de negocio de la entidad Usuario
        Raises:
            ValueError: Si alguna regla de negocio no se cumple
        """
        if not self.nombre or len(self.nombre.strip()) == 0:
            raise ValueError("El nombre del usuario es obligatorio")
        
        if len(self.nombre) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres")
        
        if not self.email or len(self.email.strip()) == 0:
            raise ValueError("El email es obligatorio")
        
        if '@' not in self.email:
            raise ValueError("El email debe ser válido")
        
        if not self.password:
            raise ValueError("La contraseña es obligatoria")
        
        if not isinstance(self.rol, RolUsuario):
            raise ValueError(f"Rol inválido. Debe ser: {[r.value for r in RolUsuario]}")
    
    def es_administrador(self) -> bool:
        """Verifica si el usuario es administrador"""
        return self.rol == RolUsuario.ADMINISTRADOR
    
    def es_externo(self) -> bool:
        """Verifica si el usuario es externo"""
        return self.rol == RolUsuario.EXTERNO
    
    def tiene_permiso(self, permiso: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico
        Los administradores tienen todos los permisos
        """
        if self.es_administrador():
            return True
        
        # Permisos limitados para externos
        permisos_externos = ['ver_productos', 'ver_inventario']
        return permiso in permisos_externos
    
    def activar(self) -> None:
        """Activa el usuario"""
        self.activo = True
    
    def desactivar(self) -> None:
        """Desactiva el usuario"""
        self.activo = False
    
    def es_activo(self) -> bool:
        """Verifica si el usuario está activo"""
        return self.activo
    
    def to_dict(self) -> dict:
        """Convierte la entidad a diccionario (sin password)"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol.value,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion,
        }
    
    @staticmethod
    def hashear_password(password_plano: str) -> str:
        """
        Hashea una contraseña
        Nota: En producción usar bcrypt o argon2
        """
        # Para el ejemplo usamos SHA256
        # En producción: usar bcrypt.hashpw()
        return hashlib.sha256(password_plano.encode()).hexdigest()
    
    @staticmethod
    def verificar_password(password_plano: str, password_hasheada: str) -> bool:
        """Verifica si una contraseña coincide con su hash"""
        return Usuario.hashear_password(password_plano) == password_hasheada
    
    @staticmethod
    def validar_password_segura(password: str) -> bool:
        """
        Valida que una contraseña cumpla requisitos de seguridad
        - Mínimo 8 caracteres
        - Al menos una letra
        - Al menos un número
        """
        if len(password) < 8:
            return False
        
        tiene_letra = any(c.isalpha() for c in password)
        tiene_numero = any(c.isdigit() for c in password)
        
        return tiene_letra and tiene_numero
    
    def __str__(self) -> str:
        return f"Usuario({self.nombre} - {self.email})"
    
    def __repr__(self) -> str:
        return f"Usuario(id={self.id}, email='{self.email}', rol={self.rol.value})"
