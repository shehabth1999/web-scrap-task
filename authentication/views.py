from rest_framework import generics
from rest_framework.permissions import AllowAny
from authentication.serializers import UserRegistrationSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


