from rest_framework.routers import DefaultRouter
from .views import TransaccionBlockchainViewSet, AuditoriaBlockchainViewSet

app_name = 'blockchain'

router = DefaultRouter()
router.register(r'transacciones', TransaccionBlockchainViewSet, basename='transaccion-blockchain')
router.register(r'auditorias', AuditoriaBlockchainViewSet, basename='auditoria-blockchain')

urlpatterns = router.urls