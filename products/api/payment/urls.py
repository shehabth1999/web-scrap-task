from django.urls import path
from .views import OrderPayment, SuccessPayment, CancelPayment

urlpatterns = [
    path('create/', OrderPayment.as_view(), name='create_order'),
    path('success/<str:token>/', SuccessPayment.as_view(), name='success_order'),
    path('cancel/<str:token>/', CancelPayment.as_view(), name='cancel_order'),
]