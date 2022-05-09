from itertools import count, product
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response

from store.pagination import DefaultPagination
from .models import Collection, Product, OrderItem, Reviews
from .serializers import CollectionSerializer, ProductSerializer, ReviewsSerializer 

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