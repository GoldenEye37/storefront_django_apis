from itertools import count, product
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
from rest_framework.response import Response

from store.pagination import DefaultPagination
from .models import Cart, CartItem, Collection, Product, OrderItem, Reviews
from .serializers import AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer, ProductSerializer, ReviewsSerializer 

class ProductViewset(ModelViewSet):

    queryset =  Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = DefaultPagination
    filterset_fields = ['collection_id']
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']


   

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count()>0:
            return Response('error')

        return super().destroy(request, *args, **kwargs)

        


class CollectionViewset(ModelViewSet):

    queryset = Collection.objects.annotate(products_count = Count('products')).all()
    serializer_class= CollectionSerializer

    def delete(self, request, pk):
        Collection.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


class ReviewsViewset(ModelViewSet):
    serializer_class = ReviewsSerializer

    def get_queryset(self):
        return Reviews.objects.filter(product_id = self.kwargs['product_pk'])
        

    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']}

class CartViewset(ModelViewSet, CreateModelMixin,RetrieveModelMixin, DestroyModelMixin, GenericViewSet):

    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewset(ModelViewSet):
    
    def get_serializer_class(self):
        if self.request.method =='GET':
            return CartItemSerializer
        elif self.request.method == 'POST':
            return AddCartItemSerializer

    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.\
            filter(cart_id = self.kwargs['cart_pk'])\
            .select_related('product')
