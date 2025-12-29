"""
Repositorio de Usuario - Implementación con Django ORM
Capa de Infraestructura
"""
from typing import Optional
from aplicacion.interfaces.repositorios import IRepositorioUsuario
from dominio.entidades.usuario import Usuario, RolUsuario
from infraestructura.django_orm.models import UsuarioModel


class RepositorioUsuarioDjango(IRepositorioUsuario):
    """Implementación del repositorio de Usuario usando Django ORM"""
    
    def guardar(self, usuario: Usuario) -> Usuario:
        """Guarda un nuevo usuario en la BD"""
        usuario_model = UsuarioModel(
            nombre=usuario.nombre,
            email=usuario.email,
            password=usuario.password,  # Ya viene hasheada
            rol=usuario.rol.value,
            activo=usuario.activo
        )
        usuario_model.save()
        usuario.id = usuario_model.id
        return usuario
    
    def obtener_por_id(self, usuario_id: int) -> Optional[dict]:
        """Obtiene un usuario por ID"""
        try:
            modelo = UsuarioModel.objects.get(id=usuario_id)
            return self._modelo_a_dict(modelo)
        except UsuarioModel.DoesNotExist:
            return None
    
    def obtener_por_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por email"""
        try:
            modelo = UsuarioModel.objects.get(email=email)
            return self._modelo_a_dict(modelo)
        except UsuarioModel.DoesNotExist:
            return None
    
    def verificar_permisos(self, usuario_id: int, permiso: str) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        usuario_data = self.obtener_por_id(usuario_id)
        if not usuario_data:
            return False
        
        # Crear entidad temporal para usar lógica del dominio
        usuario = Usuario(
            id=usuario_data['id'],
            nombre=usuario_data['nombre'],
            email=usuario_data['email'],
            password=usuario_data['password'],
            rol=RolUsuario(usuario_data['rol']),
            activo=usuario_data['activo']
        )
        
        return usuario.tiene_permiso(permiso)
    
    def _modelo_a_dict(self, modelo: UsuarioModel) -> dict:
        """Convierte un modelo Django a diccionario"""
        return {
            'id': modelo.id,
            'nombre': modelo.nombre,
            'email': modelo.email,
            'password': modelo.password,  # Incluye hash para verificación
            'rol': modelo.rol,
            'activo': modelo.activo,
            'fecha_creacion': modelo.fecha_creacion
        }
