from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def api_root(request):
    """Vista principal de la API"""
    return Response({
        'mensaje': 'Bienvenido a la API de Gestión de Inventario - Lite Thinking',
        'version': '1.0.0',
        'endpoints': {
            'autenticacion': {
                'registro': '/api/auth/registro/',
                'login': '/api/auth/login/',
                'logout': '/api/auth/logout/',
                'perfil': '/api/auth/perfil/',
                'token_refresh': '/api/auth/token/refresh/',
            },
            'empresas': '/api/empresas/',
            'productos': '/api/productos/',
            'inventario': {
                'registros': '/api/inventario/registros/',
                'movimientos': '/api/inventario/movimientos/',
                'generar_pdf': '/api/inventario/registros/generar_pdf/',
                'enviar_email': '/api/inventario/registros/enviar_pdf_email/',
            },
            'inteligencia_artificial': {
                'predicciones': '/api/ia/predicciones/',
                'chatbot': '/api/ia/chatbot/',
                'analisis': '/api/ia/analisis/',
            },
            'blockchain': {
                'transacciones': '/api/blockchain/transacciones/',
                'auditorias': '/api/blockchain/auditorias/',
            },
            'admin': '/admin/',
        }
    })

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # Apps
    path('api/auth/', include('autenticacion.urls')),
    path('api/empresas/', include('empresas.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/inventario/', include('inventario.urls')),
    path('api/ia/', include('inteligencia_artificial.urls')),
    path('api/blockchain/', include('blockchain.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar admin
admin.site.site_header = "Administración - Lite Thinking"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Gestión de Inventario"