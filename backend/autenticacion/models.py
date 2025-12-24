from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class GestorUsuario(BaseUserManager):
    """Gestor personalizado para el modelo Usuario"""
    
    def create_user(self, correo, contrasena=None, **campos_extra):
        """Crea y guarda un usuario regular"""
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        
        correo = self.normalize_email(correo)
        usuario = self.model(correo=correo, **campos_extra)
        usuario.set_password(contrasena)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, correo, contrasena=None, **campos_extra):
        """Crea y guarda un superusuario"""
        campos_extra.setdefault('is_staff', True)
        campos_extra.setdefault('is_superuser', True)
        campos_extra.setdefault('es_administrador', True)
        
        if campos_extra.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True')
        if campos_extra.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True')
        
        return self.create_user(correo, contrasena, **campos_extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado de Usuario"""
    
    TIPO_USUARIO_CHOICES = [
        ('ADMINISTRADOR', 'Administrador'),
        ('EXTERNO', 'Externo'),
    ]
    
    correo = models.EmailField(
        unique=True,
        verbose_name='Correo Electrónico'
    )
    nombre_completo = models.CharField(
        max_length=255,
        verbose_name='Nombre Completo',
        blank=True
    )
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO_CHOICES,
        default='EXTERNO',
        verbose_name='Tipo de Usuario'
    )
    es_administrador = models.BooleanField(
        default=False,
        verbose_name='Es Administrador'
    )
    esta_activo = models.BooleanField(
        default=True,
        verbose_name='Está Activo'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Es Staff'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    
    objects = GestorUsuario()
    
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.correo
    
    @property
    def is_active(self):
        """Compatibilidad con Django admin"""
        return self.esta_activo
    
    def tiene_permiso_administrador(self):
        """Verifica si el usuario tiene permisos de administrador"""
        return self.es_administrador or self.tipo_usuario == 'ADMINISTRADOR'