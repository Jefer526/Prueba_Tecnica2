from django.urls import path
from .views import IAViewSet

# No usar DefaultRouter aquí porque ya hay uno en configuracion/urls.py
# En su lugar, definir las URLs manualmente

urlpatterns = [
    # Endpoint principal del chatbot
    path('chat/', IAViewSet.as_view({'post': 'chat'}), name='ia-chat'),
    
    # Listar conversaciones del usuario
    path('conversaciones/', IAViewSet.as_view({'get': 'conversaciones'}), name='ia-conversaciones'),
    
    # Obtener conversación específica
    path('conversacion/<int:pk>/', IAViewSet.as_view({'get': 'conversacion'}), name='ia-conversacion-detalle'),
    
    # Eliminar conversación
    path('conversacion/<int:pk>/eliminar/', IAViewSet.as_view({'delete': 'eliminar_conversacion'}), name='ia-conversacion-eliminar'),
    
    # Crear nueva conversación
    path('nueva_conversacion/', IAViewSet.as_view({'post': 'nueva_conversacion'}), name='ia-nueva-conversacion'),
]