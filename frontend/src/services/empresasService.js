import api from './api';

const empresasService = {
  // Obtener todas las empresas
  obtenerTodas: async (params = {}) => {
    const respuesta = await api.get('/empresas/', { params });
    return respuesta.data;
  },

  // Obtener una empresa por NIT
  obtenerPorNit: async (nit) => {
    const respuesta = await api.get(`/empresas/${nit}/`);
    return respuesta.data;
  },

  // Crear empresa
  crear: async (datos) => {
    const respuesta = await api.post('/empresas/', datos);
    return respuesta.data;
  },

  // Actualizar empresa
  actualizar: async (nit, datos) => {
    const respuesta = await api.put(`/empresas/${nit}/`, datos);
    return respuesta.data;
  },

  // Actualización parcial
  actualizarParcial: async (nit, datos) => {
    const respuesta = await api.patch(`/empresas/${nit}/`, datos);
    return respuesta.data;
  },

  // Eliminar (desactivar) empresa
  eliminar: async (nit) => {
    const respuesta = await api.delete(`/empresas/${nit}/`);
    return respuesta.data;
  },

  // Activar empresa
  activar: async (nit) => {
    const respuesta = await api.post(`/empresas/${nit}/activar/`);
    return respuesta.data;
  },

  // Obtener estadísticas de empresa
  obtenerEstadisticas: async (nit) => {
    const respuesta = await api.get(`/empresas/${nit}/estadisticas/`);
    return respuesta.data;
  },
};

export default empresasService;
