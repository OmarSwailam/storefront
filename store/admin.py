from django.contrib import admin
from django.db.models.aggregates import Count

from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("==0", "Out of stock"), ("<10", "Low"), (">10", "In stock")]

    def queryset(self, request, queryset):
        if self.value() == "==0":
            return queryset.filter(inventory__exact=0)
        elif self.value() == "<10":
            return queryset.filter(inventory__lt=10)
        return queryset.filter(inventory__gte=10)


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ["thumbnail"]

    def thumbnail(self, instance):
        if instance.image.name != "":
            return format_html(f"<img src='{instance.image.url}' class='thumbnail'/>")
        return ""


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ["clear_inventory"]
    autocomplete_fields = ["collection"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ["title"]}
    inlines = [ProductImageInline]
    list_display = ["title", "inventory_status", "unit_price", "collection_title"]
    list_editable = ["unit_price"]
    list_per_page = 100
    list_filter = ["collection", "last_update", InventoryFilter]
    list_select_related = ["collection"]

    @admin.display(ordering="collection__title")
    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory == 0:
            return "Out of stock"
        elif product.inventory < 10:
            return "Low"
        return "In stock"

    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request, f"{updated_count} products were successfully updated"
        )

    class Media:
        css = {"all": ["store/styles.css"]}


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    autocomplete_fields = ["product"]
    min_num = 1
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    list_display = ["id", "placed_at", "payment_status", "customer_name"]
    list_select_related = ["customer"]

    inlines = [OrderItemInline]

    def customer_name(self, order):
        return order.customer


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    autocomplete_fields = ["user"]
    list_display = ["first_name", "last_name", "email", "phone", "membership", "orders"]
    list_editable = ["membership"]
    list_select_related = ["user"]
    list_per_page = 100
    search_fields = [
        "first_name__istartswith",
        "last_name__istartswith",
        "phone__istartswith",
        "email__istartswith",
    ]

    @admin.display(ordering="orders")
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html('<a href="{}">{}<a>', url, customer.orders)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders=Count("order"))


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "products_count"]
    search_fields = ["title"]
    list_per_page = 100

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html('<a href="{}">{}<a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    search_fields = ["id"]

    # @admin.display(ordering='products_count')
    # def products_count(self, collection):
    #     url = (
    #         reverse('admin:store_product_changelist')
    #         + '?'
    #         + urlencode({
    #             'collection__id': str(collection.id)
    #         }))
    #     return format_html('<a href="{}">{}<a>', url, collection.products_count)

    # def get_queryset(self, request):
    #     return super().get_queryset(request).annotate(
    #         products_count=Count('products')
    #     )


@admin.register(models.CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id"]
    search_fields = ["id"]
    list_per_page = 100

    # @admin.display(ordering='products_count')
    # def products_count(self, collection):
    #     url = (
    #         reverse('admin:store_product_changelist')
    #         + '?'
    #         + urlencode({
    #             'collection__id': str(collection.id)
    #         }))
    #     return format_html('<a href="{}">{}<a>', url, collection.products_count)

    # def get_queryset(self, request):
    #     return super().get_queryset(request).annotate(
    #         products_count=Count('products')
    #     )
