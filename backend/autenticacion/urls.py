from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegistroUsuarioView,
    LoginView,
    LogoutView,
    PerfilUsuarioView,
    CambiarContrasenaView,
    ListaUsuariosView
)

app_name = 'autenticacion'

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilUsuarioView.as_view(), name='perfil'),
    path('cambiar-contrasena/', CambiarContrasenaView.as_view(), name='cambiar-contrasena'),
    path('usuarios/', ListaUsuariosView.as_view(), name='lista-usuarios'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]