from rest_framework.routers import DefaultRouter
from .views import PrediccionPrecioViewSet, ChatbotViewSet, AnalisisInventarioViewSet

app_name = 'inteligencia_artificial'

router = DefaultRouter()
router.register(r'predicciones', PrediccionPrecioViewSet, basename='prediccion-precio')
router.register(r'chatbot', ChatbotViewSet, basename='chatbot')
router.register(r'analisis', AnalisisInventarioViewSet, basename='analisis-inventario')

urlpatterns = router.urls