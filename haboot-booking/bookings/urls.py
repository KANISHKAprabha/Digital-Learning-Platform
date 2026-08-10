from django.urls import path
from .views import *
from .payment_mock_views import *

urlpatterns=[
    path("lsas/search/",LSASearchView.as_view(),name="lsa-search"),
    path("bookings/",BookingCreateView.as_view(),name="create-booking"),
    path("mock-payments/",MockPaymentCreateView.as_view(),name="mock-payment-create"),
    path("payments/webhook/",PaymentWebHookView.as_view(),name="payment-webhook")
]