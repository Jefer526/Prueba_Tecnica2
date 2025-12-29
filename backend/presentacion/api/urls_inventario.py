"""
URLs para Inventario y Movimientos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.api.views_inventario import InventarioViewSet, MovimientoViewSet

# Crear router
router = DefaultRouter()
router.register(r'inventario', InventarioViewSet, basename='inventario')
router.register(r'movimientos', MovimientoViewSet, basename='movimientos')

urlpatterns = [
    path('', include(router.urls)),
]
