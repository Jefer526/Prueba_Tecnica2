import api from './api';

const chatbotService = {
  // Enviar mensaje al chatbot
  enviarMensaje: async (mensaje, conversacionId = null) => {
    const datos = {
      mensaje,
      conversacion_id: conversacionId,
      incluir_contexto: true
    };
    // ⭐ ACTUALIZADO: Cambiar de /ia/chat/ a /chatbot/chat/
    const respuesta = await api.post('/chatbot/chat/', datos);
    return respuesta.data;
  },

  // Obtener todas las conversaciones del usuario
  obtenerConversaciones: async () => {
    // ⭐ ACTUALIZADO: Cambiar de /ia/conversaciones/ a /chatbot/conversaciones/
    const respuesta = await api.get('/chatbot/conversaciones/');
    return respuesta.data;
  },

  // Obtener una conversación específica con sus mensajes
  obtenerConversacion: async (id) => {
    // ⭐ ACTUALIZADO: Cambiar de /ia/conversacion/ a /chatbot/conversacion/
    const respuesta = await api.get(`/chatbot/conversacion/${id}/`);
    return respuesta.data;
  },

  // Crear nueva conversación
  nuevaConversacion: async () => {
    // ⭐ ACTUALIZADO: Cambiar de /ia/nueva_conversacion/ a /chatbot/nueva/
    const respuesta = await api.post('/chatbot/nueva/');
    return respuesta.data;
  },

  // Eliminar conversación
  eliminarConversacion: async (id) => {
    // ⭐ ACTUALIZADO: Cambiar de /ia/conversacion/ a /chatbot/conversacion/
    const respuesta = await api.delete(`/chatbot/conversacion/${id}/`);
    return respuesta.data;
  },
};

export default chatbotService;