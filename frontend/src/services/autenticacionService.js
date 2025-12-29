import api from './api';

const autenticacionService = {
  // Iniciar sesión
  login: async (correo, contrasena) => {
    const respuesta = await api.post('/auth/login/', {
      email: correo,
      password: contrasena,
    });
    
    // ⭐ NUEVO: Transformar respuesta para Zustand store
    const respuestaTransformada = {
      tokens: {
        access: respuesta.data.access,
        refresh: respuesta.data.refresh,
      },
      usuario: respuesta.data.usuario,
    };
    
    // Guardar tokens manualmente también (por si acaso)
    localStorage.setItem('token_acceso', respuesta.data.access);
    localStorage.setItem('token_refresco', respuesta.data.refresh);
    localStorage.setItem('usuario', JSON.stringify(respuesta.data.usuario));
    
    return respuestaTransformada;
  },

  // Registrar usuario
  registro: async (datos) => {
    const datosRegistro = {
      email: datos.correo,
      password: datos.contrasena,
      nombre: datos.nombre_completo,
      rol: datos.tipo_usuario || 'EXTERNO',
    };
    
    console.log('Datos enviados al backend:', datosRegistro);
    
    const respuesta = await api.post('/auth/register/', datosRegistro);
    
    // ⭐ NUEVO: Transformar respuesta para Zustand store
    const respuestaTransformada = {
      tokens: {
        access: respuesta.data.access || null,
        refresh: respuesta.data.refresh || null,
      },
      usuario: respuesta.data.usuario,
    };
    
    return respuestaTransformada;
  },

  // Cerrar sesión
  logout: () => {
    localStorage.removeItem('token_acceso');
    localStorage.removeItem('token_refresco');
    localStorage.removeItem('usuario');
  },

  // Obtener perfil del usuario
  obtenerPerfil: async () => {
    const respuesta = await api.get('/auth/perfil/');
    return respuesta.data;
  },

  // Actualizar perfil
  actualizarPerfil: async (datos) => {
    const respuesta = await api.put('/auth/perfil/', datos);
    return respuesta.data;
  },

  // Cambiar contraseña
  cambiarContrasena: async (datos) => {
    const respuesta = await api.post('/auth/cambiar-contrasena/', datos);
    return respuesta.data;
  },
  
  // Verificar si está autenticado
  isAuthenticated: () => {
    return !!localStorage.getItem('token_acceso');
  },
  
  // Obtener usuario actual
  getCurrentUser: () => {
    const userStr = localStorage.getItem('usuario');
    return userStr ? JSON.parse(userStr) : null;
  },
};

export default autenticacionService;