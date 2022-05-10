from cgitb import lookup
from django.urls import path
from . import views
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

router=routers.DefaultRouter()

router.register('products', views.ProductViewset)
router.register('collections', views.CollectionViewset)
router.register('carts', views.CartViewset)

product_router = routers.NestedDefaultRouter(router, 'products',lookup = 'product')
product_router.register('reviews',views.ReviewsViewset,basename = 'product-review')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup = 'cart')
carts_router.register('items', views.CartItemViewset, basename = 'cart-items')

urlpatterns = router.urls + product_router.urls + carts_router.urls

