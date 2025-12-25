from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.routers import DefaultRouter

# Importar ViewSets
from empresas.views import EmpresaViewSet
from productos.views import ProductoViewSet
from inventario.views import InventarioViewSet, MovimientoInventarioViewSet
from inteligencia_artificial.views import PrediccionPrecioViewSet, ChatbotViewSet, AnalisisInventarioViewSet
from blockchain.views import TransaccionBlockchainViewSet, AuditoriaBlockchainViewSet

# Router único para toda la aplicación
router = DefaultRouter()

# Registrar todos los ViewSets
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'inventario/registros', InventarioViewSet, basename='registro-inventario')
router.register(r'inventario/movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')
router.register(r'ia/predicciones', PrediccionPrecioViewSet, basename='prediccion-precio')
router.register(r'ia/chatbot', ChatbotViewSet, basename='chatbot')
router.register(r'ia/analisis', AnalisisInventarioViewSet, basename='analisis-inventario')
router.register(r'blockchain/transacciones', TransaccionBlockchainViewSet, basename='transaccion-blockchain')
router.register(r'blockchain/auditorias', AuditoriaBlockchainViewSet, basename='auditoria-blockchain')

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
    
    # Autenticación (no usa router)
    path('api/auth/', include('autenticacion.urls')),
    
    # Todos los ViewSets registrados en el router
    path('api/', include(router.urls)),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalizar admin
admin.site.site_header = "Administración - Lite Thinking"
admin.site.site_title = "Panel de Administración"
admin.site.index_title = "Gestión de Inventario"