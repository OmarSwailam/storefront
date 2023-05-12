from django.conf import settings
from django.db.models.aggregates import Count
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from .models import (
    Product,
    Collection,
    OrderItem,
    Review,
    Cart,
    CartItem,
    Customer,
    Order,
    ProductImage,
)
from .serializers import (
    ProductSerializer,
    CollectionSerializer,
    ReviewSerializer,
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
    CustomerSerializer,
    OrderSerializer,
    CreateOrderSerializer,
    OrderItemSerializer,
    UpdateOrderSerializer,
    ProductImageSerializer,
)
from .filters import ProductFilter
from .pagination import DefaultPagination
from .permissions import (
    IsAdminOrReadOnly,
    ViewCustomerHistoryPermission,
)
import stripe


def get_cache_key(product_id):
    return f"product_detail_{product_id}"


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related("images").all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "unit_price", "last_updated"]

    # @method_decorator(cache_page(60 * 5))
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "cannot delete the Product because it's associated with an OrderItem"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count("products"))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "cannot delete the collection because their is a one product or more associated with it"
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_pk": self.kwargs["product_pk"]}


class CartViewSet(
    CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.prefetch_related("items__product").all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs["cart_pk"]).select_related(
            "product"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AddCartItemSerializer
        elif self.request.method == "PATCH":
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {"cart_pk": self.kwargs["cart_pk"]}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response("ok")

    @action(detail=False, methods=["GET", "PUT"], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == "GET":
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == "PUT":
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    pagination_class = DefaultPagination

    def get_permissions(self):
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(
            data=self.request.data, context={"user_id": self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        stripe.api_key = settings.STRIPE_SECRET_KEY

        line_items_list = []
        for order_item in order.items.all():
            if order_item.product.images.count() > 0:
                product_images = [
                    f"http://localhost:8000/{order_item.product.images.first().image.url}"
                ]
            # Stripe Checkout is a fully hosted solution, once you redirect to the created Checkout session
            # you're no longer working inside of your local development environment.
            # To remedy this, should pass URLs for your product images that are hosted remotely that the Checkout session can access.
            line_items_list.append(
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(order_item.product.unit_price) * 100,
                        "product_data": {
                            "name": order_item.product.title,
                            "images": product_images,
                        },
                    },
                    "quantity": order_item.quantity,
                }
            )
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items_list,
                mode="payment",
                success_url=settings.SITE_URL
                + "?success=true",  # the frontend should send a patch request to edit the order payment status
                cancel_url=settings.SITE_URL + "?canceled=true",
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return Response(
                {
                    "msg": "something went wrong while creating stripe session",
                    "error": str(e),
                },
                status=500,
            )

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related("items__product")

        customer = Customer.objects.only("id").get(user_id=user.id)
        return Order.objects.filter(customer_id=customer.id).prefetch_related(
            "items__product"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateOrderSerializer
        elif self.request.method == "PATCH":
            return UpdateOrderSerializer
        return OrderSerializer


class OrderItemViewSet(ModelViewSet):
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        items = OrderItem.objects.all().prefetch_related("orderitems")
        return items


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs["product_pk"])

    def get_serializer_context(self):
        return {"product_id": self.kwargs["product_pk"]}
