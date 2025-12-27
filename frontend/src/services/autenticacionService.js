import api from './api';

const autenticacionService = {
  // Iniciar sesión
  login: async (correo, contrasena) => {
    const respuesta = await api.post('/auth/login/', {
      correo,
      contrasena,
    });
    return respuesta.data;
  },

  // Registrar usuario
  registro: async (datos) => {
    // Asegurar que se envían todos los campos necesarios
    const datosRegistro = {
      correo: datos.correo,
      contrasena: datos.contrasena,
      confirmar_contrasena: datos.contrasena, // El backend requiere este campo
      nombre_completo: datos.nombre_completo,
      tipo_usuario: datos.tipo_usuario || 'EXTERNO',
    };
    
    console.log('Datos enviados al backend:', datosRegistro);
    
    const respuesta = await api.post('/auth/registro/', datosRegistro);
    return respuesta.data;
  },

  // Cerrar sesión
  logout: async (tokenRefresco) => {
    const respuesta = await api.post('/auth/logout/', {
      refresh_token: tokenRefresco,
    });
    return respuesta.data;
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
};

export default autenticacionService;
