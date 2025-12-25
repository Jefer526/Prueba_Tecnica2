from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet

app_name = 'productos'

router = DefaultRouter()
router.register(r'', ProductoViewSet, basename='producto')

urlpatterns = router.urls