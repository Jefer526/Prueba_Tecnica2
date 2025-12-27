import api from './api';

const iaService = {
  // Predicciones de Precio
  obtenerPredicciones: async (params = {}) => {
    const respuesta = await api.get('/ia/predicciones/', { params });
    return respuesta.data;
  },

  predecirPrecio: async (productoId) => {
    const respuesta = await api.post('/ia/predicciones/predecir_precio/', {
      producto_id: productoId,
    });
    return respuesta.data;
  },

  // Chatbot
  obtenerConsultas: async (params = {}) => {
    const respuesta = await api.get('/ia/chatbot/', { params });
    return respuesta.data;
  },

  consultarChatbot: async (pregunta) => {
    const respuesta = await api.post('/ia/chatbot/consultar/', {
      pregunta,
    });
    return respuesta.data;
  },

  // Análisis de Inventario
  obtenerAnalisis: async (params = {}) => {
    const respuesta = await api.get('/ia/analisis/', { params });
    return respuesta.data;
  },

  generarAnalisis: async () => {
    const respuesta = await api.post('/ia/analisis/generar_analisis/');
    return respuesta.data;
  },
};

export default iaService;
