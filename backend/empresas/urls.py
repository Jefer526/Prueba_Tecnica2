from rest_framework.routers import DefaultRouter
from .views import EmpresaViewSet

app_name = 'empresas'

router = DefaultRouter()
router.register(r'', EmpresaViewSet, basename='empresa')

urlpatterns = router.urls