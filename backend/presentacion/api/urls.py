"""
URLs de la API - Capa de Presentación
Define los endpoints HTTP
"""
from django.urls import path, include
from presentacion.api.views import (
    EmpresaListCreateView,
    EmpresaDetailView,
    ProductoListCreateView,
    ProductoDetailView,
    InventarioListView,
    MovimientoCreateView,
)

urlpatterns = [
    # Empresas
    path('empresas/', EmpresaListCreateView.as_view(), name='empresa-list-create'),
    path('empresas/<int:empresa_id>/', EmpresaDetailView.as_view(), name='empresa-detail'),
    
    # Productos
    path('productos/', ProductoListCreateView.as_view(), name='producto-list-create'),
    path('productos/<int:producto_id>/', ProductoDetailView.as_view(), name='producto-detail'),
    
    # Inventario
    path('inventario/', InventarioListView.as_view(), name='inventario-list'),
    
    # Movimientos
    path('movimientos/', MovimientoCreateView.as_view(), name='movimiento-create'),

    # Autenticación
    path('', include('presentacion.api.urls_auth')),

    # Chatbot
    path('', include('presentacion.api.urls_chatbot')),
]
