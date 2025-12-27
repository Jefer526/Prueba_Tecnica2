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

  // Crear producto
  crear: async (datos) => {
    const respuesta = await api.post('/productos/', datos, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return respuesta.data;
  },

  // Actualizar producto
  actualizar: async (id, datos) => {
    const respuesta = await api.put(`/productos/${id}/`, datos, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return respuesta.data;
  },

  // Eliminar (desactivar) producto
  eliminar: async (id) => {
    const respuesta = await api.delete(`/productos/${id}/`);
    return respuesta.data;
  },

  // Activar producto
  activar: async (id) => {
    const respuesta = await api.post(`/productos/${id}/activar/`);
    return respuesta.data;
  },

  // Obtener productos por empresa
  obtenerPorEmpresa: async (nit) => {
    const respuesta = await api.get('/productos/por_empresa/', {
      params: { nit },
    });
    return respuesta.data;
  },

  // Actualizar precios
  actualizarPrecios: async (id) => {
    const respuesta = await api.post(`/productos/${id}/actualizar_precios/`);
    return respuesta.data;
  },
};

export default productosService;
