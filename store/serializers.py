from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import (
    Product,
    Collection,
    Review,
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
)


class ProductSerializer(serializers.ModelSerializer):
    taxed_price = serializers.SerializerMethodField(method_name="calculate_tax")

    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "inventory",
            "unit_price",
            "taxed_price",
            "collection",
        ]

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.2)


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "name", "description", "date", "product"]

        extra_kwargs = {"product": {"read_only": True}}

    def create(self, validated_data):
        product_pk = self.context["product_pk"]
        return Review.objects.create(product_id=product_pk, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, item):
        return item.quantity * item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Wrong product id")
        return value

    def save(self, **kwargs):
        cart_id = self.context["cart_pk"]

        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
            self.instance = cart_item
        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart):
        return sum(
            [item.product.unit_price * item.quantity for item in cart.items.all()]
        )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]
        extra_kwargs = {"id": {"read_only": True}}


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "user_id", "phone", "birth_date", "membership"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, item):
        return item.quantity * item.product.unit_price

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "total_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="get_total_price")

    def get_total_price(self, cart):
        return sum(
            [item.product.unit_price * item.quantity for item in cart.items.all()]
        )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "placed_at",
            "payment_status",
            "items",
            "total_price",
        ]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        print(cart_id)
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("Wrong cart id")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            print(CartItem.objects.filter(pk=cart_id).count())
            raise serializers.ValidationError("Empty cart")
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(
                user_id=self.context["user_id"]
            )
            order = Order.objects.create(customer=customer)
            cart_id = self.validated_data["cart_id"]
            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            cart = Cart.objects.get(id=cart_id)
            cart.delete()

            order_created.send_robust(self.__class__, order=order)

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class AddOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validated_product_id(self, value):
        if not Product.objects.filter(id=self.product_id).exists():
            return serializers.ValidationError("Wrong product id")
        return value

    def save(self, **kwargs):
        order_id = self.context["order_pk"]
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        try:
            order_item = OrderItem.objects.get(order_id=order_id, product_id=product_id)
            order_item.quantity += quantity
            order_item.save()
            self.instance = order_item
        except OrderItem.DoesNotExist:
            order_item = OrderItem.objects.create(
                order_id=order_id, **self.validated_data
            )
            self.instance = order_item
        return self.instance

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "quantity"]
