"""
URLs de la API - Capa de Presentación
"""
from django.urls import path, include

urlpatterns = [
    # Autenticación
    path('', include('presentacion.api.urls_auth')),
    
    # Chatbot
    path('', include('presentacion.api.urls_chatbot')),
    
    # Empresas
    path('', include('presentacion.api.urls_empresas')),
    
    # Productos
    path('', include('presentacion.api.urls_productos')),
    
    # Inventario y Movimientos
    path('', include('presentacion.api.urls_inventario')),
]