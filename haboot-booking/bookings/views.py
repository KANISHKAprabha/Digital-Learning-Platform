from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from .services import *
from .exceptions import *
from .payment_services import *



class LSASearchView(APIView):
    def get(self,request):
        serializer=LSASearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        results=search_lsas(
            **serializer.validated_data
        )
        response_serializer=LSASearchResultSerializer(results,many=True)
        return Response(response_serializer.data,status=status.HTTP_200_OK)
    
class BookingCreateView(APIView):
    def post(self,request):
        serializer=BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            booking=create_booking(**serializer.validated_data)
        except ParentNotFoundError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        except LSANotFoundError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        except LSAUnavailableError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_409_CONFLICT
            )
        except LSANotActiveError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_409_CONFLICT
            )
        except SkillMisMatchError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payment_result=create_payment(booking_id=booking.id,amount=1000)
            booking.payment.external_payment_id=(
                payment_result["external_payment_id"]
            )
            booking.payment.save(
                update_fields=["external_payment_id","updated_at"]
            )
        except PaymentServiceError:
            return Response(
                {
                    "error":"Unable to intiate payment"
                },status=status.HTTP_502_BAD_GATEWAY
            )
        return Response(
            {
                "booking_id":booking.id,
                "status":booking.status,
                "payment_success":booking.payment.payment_status,
                "external_payment_id":(booking.payment.external_payment_id)
            },
            status=status.HTTP_201_CREATED
        )
        
        
        
class PaymentWebHookView(APIView):
    def post(Self,request):
        serializer=PaymentWebHookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            payment=process_payment_webhook(**serializer.validated_data)
        except PaymentNotFoundError as exc:
            return Response(
                {"error":str(exc)},
                status=status.HTTP_404_NOT_FOUND
            )
        except InvalidPaymentTransactionError as exc:
            return Response(
                            {"error":str(exc)},
                            status=status.HTTP_409_CONFLICT
                        )
        return Response(
            {
                "success":True,
                "payment_status":payment.payment_status,
                "booking_status":payment.booking.status
            },
            status=status.HTTP_200_OK
        )