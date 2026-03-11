#backend/coupons/views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny 
from rest_framework.response import Response
from django.utils import timezone
from .models import Coupon
from .serializers import CouponApplySerializer, CouponSerializer

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny]) # Let anyone see the coupons, but they must login to book
def list_coupons(request):
    now = timezone.now()
    # Only fetch coupons that are active and currently within their date range
    active_coupons = Coupon.objects.filter(
        active=True,
        valid_from__lte=now,
        valid_to__gte=now
    )
    serializer = CouponSerializer(active_coupons, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_coupon(request):
    serializer = CouponApplySerializer(data=request.data)
    if serializer.is_valid():
        code = serializer.validated_data['code']
        now = timezone.now()

        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                active=True,
                valid_from__lte=now,
                valid_to__gte=now 
            )
            return Response({
                'message': 'Coupon applied successfully.',
                'discount_percentage': coupon.discount_percentage,
                'code': coupon.code
            }, status=status.HTTP_200_OK)
        
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired coupon code.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
