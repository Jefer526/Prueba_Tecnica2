import api from './api';

const inventarioService = {
  // Obtener todos los registros de inventario
  obtenerRegistros: async (params = {}) => {
    const respuesta = await api.get('/inventario/', { params });
    return respuesta.data;
  },

  // ⭐ Obtener un registro de inventario por ID
  obtenerPorId: async (id) => {
    const respuesta = await api.get(`/inventario/${id}/`);
    return respuesta.data;
  },

  // Obtener productos con bajo stock
  obtenerBajoStock: async () => {
    const respuesta = await api.get('/inventario/productos_bajo_stock/');
    return respuesta.data;
  },

  // Generar PDF de inventario
  generarPDF: async () => {
    const respuesta = await api.get('/inventario/generar_pdf/');
    return respuesta.data;
  },

  // Enviar PDF por email
  enviarPDFEmail: async (correoDestino) => {
    const respuesta = await api.post('/inventario/enviar_pdf_email/', {
      correo_destino: correoDestino
    });
    return respuesta.data;
  },

  // Obtener todos los movimientos
  obtenerMovimientos: async (params = {}) => {
    const respuesta = await api.get('/movimientos/', { params });
    return respuesta.data;
  },

  // ⭐ Crear movimiento (ENTRADA, SALIDA, AJUSTE)
  crearMovimiento: async (datos) => {
    const respuesta = await api.post('/movimientos/', datos);
    return respuesta.data;
  },

  // Generar PDF de movimientos
  generarPDFMovimientos: async (params = {}) => {
    const respuesta = await api.get('/movimientos/generar_pdf/', { params });
    return respuesta.data;
  },

  // Enviar PDF de movimientos por email
  enviarPDFMovimientosEmail: async (correoDestino, params = {}) => {
    const respuesta = await api.post('/movimientos/enviar_pdf_email/', {
      correo_destino: correoDestino,
      ...params
    });
    return respuesta.data;
  },
};

export default inventarioService;