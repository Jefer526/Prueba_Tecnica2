"""
URLs del Chatbot - Capa de Presentación
Endpoints del chatbot con Clean Architecture
"""
from django.urls import path
from presentacion.api.views_chatbot import (
    ChatbotView,
    ConversacionesView,
    ConversacionDetalleView,
    NuevaConversacionView
)

urlpatterns = [
    # Endpoint principal del chatbot
    path('chatbot/chat/', ChatbotView.as_view(), name='chatbot-chat'),
    
    # Listar conversaciones del usuario
    path('chatbot/conversaciones/', ConversacionesView.as_view(), name='chatbot-conversaciones'),
    
    # Obtener/eliminar conversación específica
    path('chatbot/conversacion/<int:conversacion_id>/', ConversacionDetalleView.as_view(), name='chatbot-conversacion'),
    
    # Crear nueva conversación
    path('chatbot/nueva/', NuevaConversacionView.as_view(), name='chatbot-nueva'),
]
