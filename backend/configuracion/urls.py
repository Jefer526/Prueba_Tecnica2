"""
URLs principales - Arquitectura Limpia
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def api_root(request):
    """Vista principal de la API"""
    return Response({
        'mensaje': 'Bienvenido a la API de Gestión de Inventario - Lite Thinking',
        'version': '2.0.0 - Arquitectura Limpia',
        'arquitectura': 'Clean Architecture',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'empresas': '/api/empresas/',
                'productos': '/api/productos/',
                'inventario': '/api/inventario/',
                'movimientos': '/api/movimientos/',
            },
            'docs': {
                'empresas': {
                    'listar': 'GET /api/empresas/',
                    'crear': 'POST /api/empresas/',
                    'detalle': 'GET /api/empresas/{id}/',
                },
                'productos': {
                    'listar': 'GET /api/productos/',
                    'crear': 'POST /api/productos/',
                    'detalle': 'GET /api/productos/{id}/',
                },
                'inventario': {
                    'listar': 'GET /api/inventario/',
                },
                'movimientos': {
                    'crear': 'POST /api/movimientos/',
                }
            }
        }
    })


urlpatterns = [
    # Admin de Django
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # API de Arquitectura Limpia
    path('api/', include('presentacion.api.urls')),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar admin
admin.site.site_header = "Administración - Lite Thinking (Clean Architecture)"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Gestión de Inventario"