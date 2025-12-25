from rest_framework.routers import DefaultRouter
from .views import InventarioViewSet, MovimientoInventarioViewSet

app_name = 'inventario'

router = DefaultRouter()
router.register(r'registros', InventarioViewSet, basename='registro-inventario')
router.register(r'movimientos', MovimientoInventarioViewSet, basename='movimiento-inventario')

urlpatterns = router.urls