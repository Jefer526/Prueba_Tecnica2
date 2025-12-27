import api from './api';

const blockchainService = {
  // Transacciones
  obtenerTransacciones: async (params = {}) => {
    const respuesta = await api.get('/blockchain/transacciones/', { params });
    return respuesta.data;
  },

  obtenerTransaccionPorId: async (id) => {
    const respuesta = await api.get(`/blockchain/transacciones/${id}/`);
    return respuesta.data;
  },

  registrarMovimiento: async (movimientoId) => {
    const respuesta = await api.post('/blockchain/transacciones/registrar_movimiento/', {
      movimiento_id: movimientoId,
    });
    return respuesta.data;
  },

  obtenerDetallesBlockchain: async (id) => {
    const respuesta = await api.get(`/blockchain/transacciones/${id}/detalles_blockchain/`);
    return respuesta.data;
  },

  obtenerEstadisticas: async () => {
    const respuesta = await api.get('/blockchain/transacciones/estadisticas/');
    return respuesta.data;
  },

  // Auditorías
  obtenerAuditorias: async (params = {}) => {
    const respuesta = await api.get('/blockchain/auditorias/', { params });
    return respuesta.data;
  },

  auditarTransaccion: async (hashTransaccion) => {
    const respuesta = await api.post('/blockchain/auditorias/auditar_transaccion/', {
      hash_transaccion: hashTransaccion,
    });
    return respuesta.data;
  },

  auditarTodas: async () => {
    const respuesta = await api.post('/blockchain/auditorias/auditar_todas/');
    return respuesta.data;
  },

  obtenerReporteIntegridad: async () => {
    const respuesta = await api.get('/blockchain/auditorias/reporte_integridad/');
    return respuesta.data;
  },
};

export default blockchainService;
