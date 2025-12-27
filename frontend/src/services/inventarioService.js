import api from './api';

const inventarioService = {
  // Registros de Inventario
  obtenerRegistros: async (params = {}) => {
    const respuesta = await api.get('/inventario/registros/', { params });
    return respuesta.data;
  },

  obtenerRegistroPorId: async (id) => {
    const respuesta = await api.get(`/inventario/registros/${id}/`);
    return respuesta.data;
  },

  crearRegistro: async (datos) => {
    const respuesta = await api.post('/inventario/registros/', datos);
    return respuesta.data;
  },

  actualizarRegistro: async (id, datos) => {
    const respuesta = await api.put(`/inventario/registros/${id}/`, datos);
    return respuesta.data;
  },

  eliminarRegistro: async (id) => {
    const respuesta = await api.delete(`/inventario/registros/${id}/`);
    return respuesta.data;
  },

  // Obtener inventario por empresa
  obtenerPorEmpresa: async (nit = null) => {
    const params = nit ? { nit } : {};
    const respuesta = await api.get('/inventario/registros/por_empresa/', { params });
    return respuesta.data;
  },

  // Productos bajo stock
  obtenerBajoStock: async () => {
    const respuesta = await api.get('/inventario/registros/productos_bajo_stock/');
    return respuesta.data;
  },

  // Generar PDF
  generarPDF: async (empresaNit = null) => {
    const datos = empresaNit ? { empresa_nit: empresaNit } : {};
    const respuesta = await api.post('/inventario/registros/generar_pdf/', datos);
    return respuesta.data;
  },

  // Enviar PDF por email
  enviarPDFEmail: async (correoDestino, empresaNit = null) => {
    const datos = {
      correo_destino: correoDestino,
    };
    if (empresaNit) {
      datos.empresa_nit = empresaNit;
    }
    const respuesta = await api.post('/inventario/registros/enviar_pdf_email/', datos);
    return respuesta.data;
  },

  // Movimientos de Inventario
  obtenerMovimientos: async (params = {}) => {
    const respuesta = await api.get('/inventario/movimientos/', { params });
    return respuesta.data;
  },

  crearMovimiento: async (datos) => {
    const respuesta = await api.post('/inventario/movimientos/', datos);
    return respuesta.data;
  },

  // Generar PDF de movimientos
  generarPDFMovimientos: async (filtros = {}) => {
    const respuesta = await api.post('/inventario/movimientos/generar_pdf/', filtros);
    return respuesta.data;
  },

  // Enviar PDF de movimientos por email
  enviarPDFMovimientosEmail: async (correoDestino, filtros = {}) => {
    const datos = {
      correo_destino: correoDestino,
      ...filtros
    };
    const respuesta = await api.post('/inventario/movimientos/enviar_pdf_email/', datos);
    return respuesta.data;
  },
};

export default inventarioService;