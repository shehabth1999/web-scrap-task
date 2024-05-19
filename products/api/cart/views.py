# rest_framework
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from django_filters.rest_framework import DjangoFilterBackend

# models
from products.models import Cart, Order

# serializers
from products.api.serializers import CartSerializer, OrderSerializer

# pagination
from products.api.pagination import CartResultsSetPagination

# filters
from products.api.filters import OrderFilter

# others
from django.db.models import Sum

# ______________________________________________________________________________ #

class CartViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    
    queryset = Cart.objects.all().order_by('-id')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CartResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def filter_queryset(self, queryset):
        return queryset.filter(user=self.request.user, status_accepted=False)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_paginated_response(self, data):
        """
        Return a paginated style response with the total price included.
        """
        total_price = Cart.objects.filter(user=self.request.user, status_accepted=False).aggregate(Sum('price'))['price__sum'] or 0.0
        response = self.paginator.get_paginated_response(data)
        response.data['total_price'] = total_price
        return response
    

# ______________________________________________________________________________ #

class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CartResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def filter_queryset(self, queryset):
        # Apply the DjangoFilterBackend filter
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        filtered_queryset = queryset.filter(cart__user=user).distinct()
        return filtered_queryset

    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    

# ______________________________________________________________________________ #


