from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken
from authentication.views import UserRegistrationView


urlpatterns = [
    path('login/', ObtainAuthToken.as_view()),
    path('register/', UserRegistrationView.as_view(), name='register'),
]