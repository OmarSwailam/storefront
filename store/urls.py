from django.urls import path
from rest_framework_nested import routers
from .views import ProductsViewSet, CollectionsViewSet, ReviewViewSet

router = routers.DefaultRouter()
router.register('products', ProductsViewSet, basename='products')
router.register('collections', CollectionsViewSet)

products_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
products_router.register('reviews', ReviewViewSet, basename='product-review')


urlpatterns = router.urls + products_router.urls
