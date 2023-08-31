from django.urls import path, include
from core.views import RegisterUserViewset

urlpatterns = [
    path('register/', RegisterUserViewset.as_view({'post': 'create'}), name="register user")
]
