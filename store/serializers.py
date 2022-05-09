from calendar import c
from decimal import Decimal
from itertools import count, product
from multiprocessing import context
from pyexpat import model
from unittest.util import _MAX_LENGTH
from rest_framework import serializers

from store.models import Collection, Product, Reviews

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']

    product_count = serializers.IntegerField(read_only=True)
    
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','slug', 'inventory', 'unit_price', 'collection', 'price_with_tax' ]

    price_with_tax = serializers.SerializerMethodField(method_name='with_tax')
    
    def with_tax(self, product:Product):
        return product.unit_price * Decimal(1.1)



class ReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = ['id','date', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']

        return Reviews.objects.create(product_id = product_id, **validated_data)

