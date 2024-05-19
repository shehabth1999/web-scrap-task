from django.urls import path, include


urlpatterns = [
    path('', include('products.api.cart.urls')),
    path('payment/', include('products.api.payment.urls')),
]
