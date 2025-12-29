"""
URLs para Empresas
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from presentacion.api.views_empresas import EmpresaViewSet

router = DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresas')

urlpatterns = [
    path('', include(router.urls)),
]
