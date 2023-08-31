from django.shortcuts import render
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from core.serializers import UserCreateSerializer
from rest_framework.permissions import AllowAny


# Create your views here.
class RegisterUserViewset(GenericViewSet, CreateModelMixin):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]


# class ForgotPaswordViewSet(GenericViewSet, UpdateModelMixin):
#     serializer_class = ResestOrUpdatePasswordSerializer
#     permission_classes = [AllowAny]
