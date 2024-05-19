from rest_framework import serializers
from products.models import Cart, Order
from django.db.models import Sum

class ProductLinkSerializer(serializers.Serializer):
    product_link = serializers.URLField()

    def validate_product_link(self, value):
        if not value.startswith('https://www.amazon.com'):
            raise serializers.ValidationError('Not supported Market')
        return value
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['market'] = 1
        return representation


class CartSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    market = serializers.CharField(source='market.name', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'

    def get_total_price(self, obj):
        user = self.context['request'].user
        queryset = Cart.objects.filter(user=user, status_accepted=False)
        return queryset.aggregate(Sum('price'))['price__sum'] or 0.0



class SelectOrderPaymentSerializer(serializers.Serializer):
    products = serializers.ListField(
        child=serializers.IntegerField()
    )

    def validate_products(self, value):
        user = self.context['request'].user
        if not value :
            raise serializers.ValidationError("No products selected")
        for product_id in value:
            if not Cart.objects.filter(id=product_id, user=user).exists():
                raise serializers.ValidationError(f"Product does not belong to the auth user")

        # Check for uniqueness
        non_unique_products = Cart.objects.filter(id__in=value, orders__isnull=False).distinct()
        if non_unique_products.exists():
            raise serializers.ValidationError("One or more cart items are already associated with an order")
        
        return value



class OrderSerializer(serializers.ModelSerializer):
    cart = CartSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'cart', 'is_paid', 'is_arrived', 'rate', 'created_at', 'total_price']

    def get_total_price(self, obj):
        # Calculate the sum of the prices of all products in the cart
        return sum(cart.price for cart in obj.cart.all())