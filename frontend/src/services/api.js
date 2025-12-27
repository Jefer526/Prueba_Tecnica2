import axios from 'axios';

// URL base de la API
const URL_BASE_API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Crear instancia de axios
const api = axios.create({
  baseURL: URL_BASE_API,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar el token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token_acceso');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const solicitudOriginal = error.config;

    // Si el error es 401 y no hemos intentado refrescar el token
    if (error.response?.status === 401 && !solicitudOriginal._retry) {
      solicitudOriginal._retry = true;

      try {
        const tokenRefresco = localStorage.getItem('token_refresco');
        const respuesta = await axios.post(`${URL_BASE_API}/auth/token/refresh/`, {
          refresh: tokenRefresco,
        });

        const nuevoToken = respuesta.data.access;
        localStorage.setItem('token_acceso', nuevoToken);

        solicitudOriginal.headers.Authorization = `Bearer ${nuevoToken}`;
        return api(solicitudOriginal);
      } catch (errorRefresco) {
        // Si falla el refresh, limpiar tokens y redirigir al login
        localStorage.removeItem('token_acceso');
        localStorage.removeItem('token_refresco');
        localStorage.removeItem('usuario');
        window.location.href = '/login';
        return Promise.reject(errorRefresco);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
