"""
Casos de Uso de Autenticación - Capa de Aplicación
Lógica de aplicación sin dependencias de Django
"""
from typing import Dict, Optional
from aplicacion.interfaces.repositorios import IRepositorioUsuario
from dominio.entidades.usuario import Usuario, RolUsuario
from dominio.excepciones.excepciones_negocio import (
    UsuarioNoEncontrado,
    CredencialesInvalidas,
    DatosInvalidos,
    EmailDuplicado
)


class RegistrarUsuarioCasoDeUso:
    """
    Caso de uso para registrar un nuevo usuario
    Reglas:
    - El email debe ser único
    - La contraseña debe ser segura
    - Se hashea la contraseña antes de guardar
    """
    
    def __init__(self, repositorio_usuario: IRepositorioUsuario):
        self.repositorio_usuario = repositorio_usuario
    
    def ejecutar(self, datos: dict) -> dict:
        """
        Registra un nuevo usuario
        
        Args:
            datos: {
                'nombre': str,
                'email': str,
                'password': str,
                'rol': str (opcional, default EXTERNO)
            }
        
        Returns:
            {
                'usuario': dict,
                'mensaje': str
            }
        
        Raises:
            EmailDuplicado: Si el email ya existe
            DatosInvalidos: Si los datos son inválidos
        """
        # 1. Validar que el email no exista
        usuario_existente = self.repositorio_usuario.obtener_por_email(datos['email'])
        if usuario_existente:
            raise EmailDuplicado(f"El email {datos['email']} ya está registrado")
        
        # 2. Validar contraseña segura
        if not Usuario.validar_password_segura(datos['password']):
            raise DatosInvalidos(
                "La contraseña debe tener mínimo 8 caracteres, "
                "al menos una letra y un número"
            )
        
        # 3. Hashear contraseña
        password_hasheada = Usuario.hashear_password(datos['password'])
        
        # 4. Determinar rol (default: EXTERNO)
        rol_str = datos.get('rol', 'EXTERNO')
        try:
            rol = RolUsuario(rol_str)
        except ValueError:
            raise DatosInvalidos(f"Rol inválido: {rol_str}")
        
        # 5. Crear entidad Usuario (ejecuta validaciones)
        usuario = Usuario(
            nombre=datos['nombre'],
            email=datos['email'],
            password=password_hasheada,
            rol=rol
        )
        
        # 6. Persistir usuario
        usuario_guardado = self.repositorio_usuario.guardar(usuario)
        
        # 7. Retornar resultado (sin password)
        return {
            'usuario': usuario_guardado.to_dict(),
            'mensaje': f'Usuario {usuario_guardado.email} registrado exitosamente'
        }


class IniciarSesionCasoDeUso:
    """
    Caso de uso para iniciar sesión
    Reglas:
    - El usuario debe existir
    - El usuario debe estar activo
    - La contraseña debe ser correcta
    """
    
    def __init__(self, repositorio_usuario: IRepositorioUsuario):
        self.repositorio_usuario = repositorio_usuario
    
    def ejecutar(self, datos: dict) -> dict:
        """
        Inicia sesión de un usuario
        
        Args:
            datos: {
                'email': str,
                'password': str
            }
        
        Returns:
            {
                'usuario': dict,
                'mensaje': str
            }
        
        Raises:
            UsuarioNoEncontrado: Si el email no existe
            CredencialesInvalidas: Si la contraseña es incorrecta
        """
        # 1. Obtener usuario por email
        usuario_data = self.repositorio_usuario.obtener_por_email(datos['email'])
        
        if not usuario_data:
            raise UsuarioNoEncontrado(f"No existe usuario con email {datos['email']}")
        
        # 2. Verificar que esté activo
        if not usuario_data.get('activo', False):
            raise CredencialesInvalidas("Usuario inactivo")
        
        # 3. Verificar contraseña
        password_correcta = Usuario.verificar_password(
            datos['password'],
            usuario_data['password']
        )
        
        if not password_correcta:
            raise CredencialesInvalidas("Contraseña incorrecta")
        
        # 4. Retornar usuario autenticado (sin password)
        usuario_autenticado = {
            'id': usuario_data['id'],
            'nombre': usuario_data['nombre'],
            'email': usuario_data['email'],
            'rol': usuario_data['rol'],
            'activo': usuario_data['activo']
        }
        
        return {
            'usuario': usuario_autenticado,
            'mensaje': 'Inicio de sesión exitoso'
        }


class ObtenerPerfilCasoDeUso:
    """
    Caso de uso para obtener el perfil del usuario autenticado
    """
    
    def __init__(self, repositorio_usuario: IRepositorioUsuario):
        self.repositorio_usuario = repositorio_usuario
    
    def ejecutar(self, usuario_id: int) -> dict:
        """
        Obtiene el perfil del usuario
        
        Args:
            usuario_id: ID del usuario autenticado
        
        Returns:
            {
                'usuario': dict
            }
        
        Raises:
            UsuarioNoEncontrado: Si el usuario no existe
        """
        # Obtener usuario
        usuario_data = self.repositorio_usuario.obtener_por_id(usuario_id)
        
        if not usuario_data:
            raise UsuarioNoEncontrado(f"Usuario con ID {usuario_id} no encontrado")
        
        # Retornar perfil (sin password)
        return {
            'usuario': {
                'id': usuario_data['id'],
                'nombre': usuario_data['nombre'],
                'email': usuario_data['email'],
                'rol': usuario_data['rol'],
                'activo': usuario_data['activo']
            }
        }
