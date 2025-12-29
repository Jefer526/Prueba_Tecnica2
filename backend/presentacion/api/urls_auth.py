"""
URLs de Autenticación - Capa de Presentación
Endpoints de registro, login y perfil
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from presentacion.api.views_auth import (
    RegistrarUsuarioView,
    IniciarSesionView,
    ObtenerPerfilView,
)

urlpatterns = [
    # Registro
    path('auth/register/', RegistrarUsuarioView.as_view(), name='auth-register'),
    
    # Login
    path('auth/login/', IniciarSesionView.as_view(), name='auth-login'),
    
    # Perfil (requiere autenticación)
    path('auth/perfil/', ObtenerPerfilView.as_view(), name='auth-perfil'),
    
    # Refresh token (JWT)
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
