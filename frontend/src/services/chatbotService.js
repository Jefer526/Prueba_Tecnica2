import api from './api';

const chatbotService = {
  // Enviar mensaje al chatbot
  enviarMensaje: async (mensaje, conversacionId = null) => {
    const datos = {
      mensaje,
      conversacion_id: conversacionId,
      incluir_contexto: true
    };
    const respuesta = await api.post('/ia/chat/', datos);
    return respuesta.data;
  },

  // Obtener todas las conversaciones del usuario
  obtenerConversaciones: async () => {
    const respuesta = await api.get('/ia/conversaciones/');
    return respuesta.data;
  },

  // Obtener una conversación específica con sus mensajes
  obtenerConversacion: async (id) => {
    const respuesta = await api.get(`/ia/conversacion/${id}/`);
    return respuesta.data;
  },

  // Crear nueva conversación
  nuevaConversacion: async () => {
    const respuesta = await api.post('/ia/nueva_conversacion/');
    return respuesta.data;
  },

  // Eliminar conversación
  eliminarConversacion: async (id) => {
    const respuesta = await api.delete(`/ia/conversacion/${id}/`);
    return respuesta.data;
  },
};

export default chatbotService;
