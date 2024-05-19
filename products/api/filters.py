import django_filters
from products.models import Order

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'is_paid': ['exact'],
        }
