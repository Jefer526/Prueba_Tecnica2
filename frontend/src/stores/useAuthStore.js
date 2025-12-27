import { create } from 'zustand';
import autenticacionService from '../services/autenticacionService';
import { jwtDecode } from 'jwt-decode';

const useAuthStore = create((set, get) => ({
  // Estado
  usuario: JSON.parse(localStorage.getItem('usuario')) || null,
  tokenAcceso: localStorage.getItem('token_acceso') || null,
  tokenRefresco: localStorage.getItem('token_refresco') || null,
  estaAutenticado: !!localStorage.getItem('token_acceso'),
  estaCargando: false,
  error: null,

  // Acciones
  login: async (correo, contrasena) => {
    try {
      set({ estaCargando: true, error: null });

      const respuesta = await autenticacionService.login(correo, contrasena);

      // Guardar tokens y usuario
      localStorage.setItem('token_acceso', respuesta.tokens.access);
      localStorage.setItem('token_refresco', respuesta.tokens.refresh);
      localStorage.setItem('usuario', JSON.stringify(respuesta.usuario));

      set({
        usuario: respuesta.usuario,
        tokenAcceso: respuesta.tokens.access,
        tokenRefresco: respuesta.tokens.refresh,
        estaAutenticado: true,
        estaCargando: false,
        error: null,
      });

      return respuesta;
    } catch (error) {
      const mensajeError = error.response?.data?.detail || 'Error al iniciar sesión';
      set({
        error: mensajeError,
        estaCargando: false,
      });
      throw error;
    }
  },

  registro: async (datos) => {
    try {
      set({ estaCargando: true, error: null });

      const respuesta = await autenticacionService.registro(datos);

      // Guardar tokens y usuario
      localStorage.setItem('token_acceso', respuesta.tokens.access);
      localStorage.setItem('token_refresco', respuesta.tokens.refresh);
      localStorage.setItem('usuario', JSON.stringify(respuesta.usuario));

      set({
        usuario: respuesta.usuario,
        tokenAcceso: respuesta.tokens.access,
        tokenRefresco: respuesta.tokens.refresh,
        estaAutenticado: true,
        estaCargando: false,
        error: null,
      });

      return respuesta;
    } catch (error) {
      const mensajeError = error.response?.data?.detail || 'Error al registrar usuario';
      set({
        error: mensajeError,
        estaCargando: false,
      });
      throw error;
    }
  },

  logout: async () => {
    try {
      const tokenRefresco = get().tokenRefresco;
      if (tokenRefresco) {
        await autenticacionService.logout(tokenRefresco);
      }
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      // Limpiar estado y localStorage
      localStorage.removeItem('token_acceso');
      localStorage.removeItem('token_refresco');
      localStorage.removeItem('usuario');

      set({
        usuario: null,
        tokenAcceso: null,
        tokenRefresco: null,
        estaAutenticado: false,
        error: null,
      });
    }
  },

  actualizarPerfil: async (datos) => {
    try {
      set({ estaCargando: true, error: null });

      const respuesta = await autenticacionService.actualizarPerfil(datos);

      // Actualizar usuario en localStorage
      localStorage.setItem('usuario', JSON.stringify(respuesta));

      set({
        usuario: respuesta,
        estaCargando: false,
        error: null,
      });

      return respuesta;
    } catch (error) {
      const mensajeError = error.response?.data?.detail || 'Error al actualizar perfil';
      set({
        error: mensajeError,
        estaCargando: false,
      });
      throw error;
    }
  },

  verificarToken: () => {
    const token = get().tokenAcceso;
    if (!token) {
      get().logout();
      return false;
    }

    try {
      const decoded = jwtDecode(token);
      const tiempoActual = Date.now() / 1000;

      if (decoded.exp < tiempoActual) {
        // Token expirado
        get().logout();
        return false;
      }

      return true;
    } catch (error) {
      get().logout();
      return false;
    }
  },

  esAdministrador: () => {
    const usuario = get().usuario;
    return usuario?.es_administrador || usuario?.tipo_usuario === 'ADMINISTRADOR';
  },

  limpiarError: () => set({ error: null }),
}));

export default useAuthStore;
