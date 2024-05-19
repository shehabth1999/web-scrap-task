# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# models
from products.models import Cart, Order

# serializers
from products.api.serializers import SelectOrderPaymentSerializer

# others
import shortuuid

# ______________________________________________________________________________ #


class OrderPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = SelectOrderPaymentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            token = shortuuid.uuid()
            product_ids = serializer.validated_data['products']
            products = Cart.objects.filter(id__in=product_ids)

            # Create and save the order before setting the many-to-many relationship
            order = Order.objects.create(token=token)
            order.cart.set(products)
            order.save()

            return Response({"payment_link": f"http://127.0.0.1:8000/cart/payment/success/{token}/"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class SuccessPayment(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')

        try:
            order = Order.objects.get(token=token)
            products = order.cart.all()
            for product in products:
                if product.status_accepted:
                    return Response({"error": "Product already accepted"}, status=status.HTTP_400_BAD_REQUEST)
                product.accept_product()
            order.paid()    
            return Response({"status": "Payment successful", 'order_id': order.pk}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
class CancelPayment(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"status": "Payment cancelled"}, status=status.HTTP_200_OK)