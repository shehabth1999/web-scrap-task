from django.urls import path
from .views import CartViewSet, OrderViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pending', CartViewSet, basename='cart')
router.register(r'order', OrderViewSet, basename='order')


urlpatterns = router.urls
