from calendar import c
from dataclasses import fields
from decimal import Decimal
from itertools import count, product
from multiprocessing import context
from pyexpat import model
from unittest.util import _MAX_LENGTH
from xml.dom import ValidationErr
from django.forms import UUIDField
from requests import delete
from django.db import transaction
from rest_framework import serializers

from store.models import Collection, Customer, Order, OrderItem, Product, Reviews, Cart, CartItem

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

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cartitem: CartItem):
        return cartitem.quantity * cartitem.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id','product', 'quantity', 'total_price']

class AddCartItemSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(read_only=True)

    def validate_product_id(self,value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given ID found!')
        return value

    def save(self, **kwargs):
        product_id = self.validated_data['product_id']
        quantity=self.validated_data['quantity']
        return super().save(**kwargs)

        try:
            cart_item = CartItem.objects.get(cart_id = cart_id, product_id = product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id = cart_id, **self.validated_data)
            
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class CartSerializer(serializers.ModelSerializer):

    id =serializers.UUIDField(read_only = True)
    items = CartItemSerializer(many=True, read_only = True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

class CustomerSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField()

    class Meta:
        model = Customer
        fields = ['id', 'user_id','phone','birth_date', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'oder', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)


    class Meta:
        model = Order
        fields= ['id', 'customer', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):

    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found!')
        if CartItem.objects.filter(cart_id=cart_id).count()==0:
            raise serializers.ValidationError('the cart is empty!')
        return cart_id

    def save(self, **kwargs):

        with transaction.atomic():
            
            cart_id = self.validated_data['cart_id']

            (customer, created) = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects \
                            .select_related('product') \
                            .filter(cart_id = cart_id)

            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.unit_price,
                    quantity = item.quantity
                ) 
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            return order