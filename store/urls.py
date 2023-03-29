from django.urls import path
from rest_framework_nested import routers
from .views import (
    ProductViewSet,
    CollectionViewSet,
    ReviewViewSet,
    CartViewSet,
    CartItemViewSet,
    CustomerViewSet
)

router = routers.DefaultRouter()
router.register("products", ProductViewSet, basename="products")
router.register("collections", CollectionViewSet)
router.register("carts", CartViewSet, basename="carts")
router.register("customers", CustomerViewSet, basename="customers")


products_router = routers.NestedDefaultRouter(
    router, "products", lookup="product")
products_router.register("reviews", ReviewViewSet, basename="product-review")


carts_router = routers.NestedDefaultRouter(router, "carts", lookup="cart")
carts_router.register("items", CartItemViewSet, basename="cart-items")

urlpatterns = router.urls + products_router.urls + carts_router.urls
