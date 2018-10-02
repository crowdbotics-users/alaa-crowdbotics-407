from django.shortcuts import render

# Create your views here.
from rest_framework.viewsets import ModelViewSet

from core.api.serializers import SignupSerializer


class SignupViewSet(ModelViewSet):
    serializer_class = SignupSerializer
    http_method_names = ['post']
