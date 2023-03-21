from decimal import Decimal
from rest_framework import serializers
from .models import Product, Collection


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']

    products_count = serializers.IntegerField(read_only=True)


class ProductSerializer(serializers.ModelSerializer):
    taxed_price = serializers.SerializerMethodField(
        method_name='calculate_tax')

    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    class Meta:
        model = Product
        fields = ['id', 'title', 'slug', 'description',
                  'inventory', 'unit_price', 'taxed_price', 'collection']

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.2)
