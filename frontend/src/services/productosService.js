import api from './api';

const productosService = {
  // Obtener todos los productos
  obtenerTodos: async (params = {}) => {
    const respuesta = await api.get('/productos/', { params });
    return respuesta.data;
  },

  // Obtener un producto por ID
  obtenerPorId: async (id) => {
    const respuesta = await api.get(`/productos/${id}/`);
    return respuesta.data;
  },

  // Crear producto (backend genera código automáticamente)
  crear: async (datos) => {
    const respuesta = await api.post('/productos/', datos);
    return respuesta.data;
  },

  // Actualizar producto (usa ID)
  actualizar: async (id, datos) => {
    const respuesta = await api.put(`/productos/${id}/`, datos);
    return respuesta.data;
  },

  // Actualización parcial
  actualizarParcial: async (id, datos) => {
    const respuesta = await api.patch(`/productos/${id}/`, datos);
    return respuesta.data;
  },

  // Eliminar (hard delete) producto
  eliminar: async (id) => {
    const respuesta = await api.delete(`/productos/${id}/`);
    return respuesta.data;
  },

  // ⭐ Activar producto
  activar: async (id) => {
    const respuesta = await api.post(`/productos/${id}/activar/`);
    return respuesta.data;
  },

  // ⭐ Inactivar producto (NUEVO)
  inactivar: async (id) => {
    const respuesta = await api.post(`/productos/${id}/inactivar/`);
    return respuesta.data;
  },

  // Obtener productos por empresa
  obtenerPorEmpresa: async (empresaNit) => {
    const respuesta = await api.get(`/productos/`, {
      params: { empresa: empresaNit }
    });
    return respuesta.data;
  },
};

export default productosService;