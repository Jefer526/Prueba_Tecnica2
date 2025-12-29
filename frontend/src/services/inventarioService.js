import api from './api';

const inventarioService = {
  // ⭐ ACTUALIZADO: Usar endpoint correcto /inventario/ en lugar de /inventario/registros/
  
  // Obtener inventarios
  obtenerRegistros: async (params = {}) => {
    const respuesta = await api.get('/inventario/', { params });
    return respuesta.data;
  },

  obtenerRegistroPorId: async (id) => {
    const respuesta = await api.get(`/inventario/${id}/`);
    return respuesta.data;
  },

  crearRegistro: async (datos) => {
    const respuesta = await api.post('/inventario/', datos);
    return respuesta.data;
  },

  actualizarRegistro: async (id, datos) => {
    const respuesta = await api.put(`/inventario/${id}/`, datos);
    return respuesta.data;
  },

  eliminarRegistro: async (id) => {
    const respuesta = await api.delete(`/inventario/${id}/`);
    return respuesta.data;
  },

  // ⭐ DESHABILITADO temporalmente - endpoint no implementado
  // Obtener inventario por empresa
  obtenerPorEmpresa: async (nit = null) => {
    const params = nit ? { nit } : {};
    const respuesta = await api.get('/inventario/', { params });
    return respuesta.data;
  },

  // ⭐ DESHABILITADO temporalmente - usar chatbot en su lugar
  // Productos bajo stock - usar el chatbot para esta funcionalidad
  obtenerBajoStock: async () => {
    // Por ahora retornar array vacío
    // Esta funcionalidad está disponible a través del chatbot
    console.warn('obtenerBajoStock: Usar chatbot para consultar productos bajo stock');
    return [];
  },

  // ⭐ DESHABILITADO temporalmente - endpoints no implementados
  // Generar PDF
  generarPDF: async (empresaNit = null) => {
    console.warn('generarPDF: Funcionalidad no disponible actualmente');
    return { mensaje: 'Funcionalidad no disponible' };
  },

  // Enviar PDF por email
  enviarPDFEmail: async (correoDestino, empresaNit = null) => {
    console.warn('enviarPDFEmail: Funcionalidad no disponible actualmente');
    return { mensaje: 'Funcionalidad no disponible' };
  },

  // ⭐ ACTUALIZADO: Movimientos de Inventario
  obtenerMovimientos: async (params = {}) => {
    const respuesta = await api.get('/movimientos/', { params });
    return respuesta.data;
  },

  crearMovimiento: async (datos) => {
    const respuesta = await api.post('/movimientos/', datos);
    return respuesta.data;
  },

  // ⭐ DESHABILITADO temporalmente - endpoints no implementados
  generarPDFMovimientos: async (filtros = {}) => {
    console.warn('generarPDFMovimientos: Funcionalidad no disponible actualmente');
    return { mensaje: 'Funcionalidad no disponible' };
  },

  enviarPDFMovimientosEmail: async (correoDestino, filtros = {}) => {
    console.warn('enviarPDFMovimientosEmail: Funcionalidad no disponible actualmente');
    return { mensaje: 'Funcionalidad no disponible' };
  },
};

export default inventarioService;