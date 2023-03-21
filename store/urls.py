from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductsViewSet, CollectionsViewSet

router = DefaultRouter()
router.register('products', ProductsViewSet)
router.register('collections', CollectionsViewSet)

urlpatterns = router.urls
