from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class MockPaymentCreateView(APIView):
    def post(self,request):
        booking_id=request.data.get("booking_id")
        amount =request.data.get("amount")
        if not booking_id or amount is None:
            return Response(
                {
                    "error":"booking_id and amount is required",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {
                "success":True,
                "external_payment_id":f"mock_pay_{booking_id}",
                "status":"PENDING"
            },
            status=status.HTTP_201_CREATED
            
            
        )