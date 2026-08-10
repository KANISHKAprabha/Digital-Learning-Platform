import pytest
from rest_framework.test import APIClient

from bookings.models import  *


@pytest.mark.django_db
def test_payment_success_webhook_confirms_booking():

    parent = Parent.objects.create(
        name="Payment Parent",
        email="paymentsuccess@example.com",
    )

    lsa = LSAProfile.objects.create(
        name="Payment LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name="Payment Child",
        start_time="2026-08-20T10:00:00Z",
        end_time="2026-08-20T11:00:00Z",
        status=BookingStatus.PENDING,
    )

    payment = Payment.objects.create(
        booking=booking,
        payment_status=PaymentStatus.PENDING,
        external_payment_id="test_payment_success",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        {
            "external_payment_id": "test_payment_success",
            "status": "SUCCESS",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    booking.refresh_from_db()

    assert payment.payment_status == PaymentStatus.SUCCESS
    assert booking.status == BookingStatus.CONFIRMED
    
    
    
    
@pytest.mark.django_db
def test_payment_failed_webhook_keeps_booking_pending():

    parent = Parent.objects.create(
        name="Payment Failure Parent",
        email="paymentfailure@example.com",
    )

    lsa = LSAProfile.objects.create(
        name="Payment Failure LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )

    booking = BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name="Payment Failure Child",
        start_time="2026-08-20T12:00:00Z",
        end_time="2026-08-20T13:00:00Z",
        status=BookingStatus.PENDING,
    )

    payment = Payment.objects.create(
        booking=booking,
        payment_status=PaymentStatus.PENDING,
        external_payment_id="test_payment_failed",
    )

    client = APIClient()

    response = client.post(
        "/api/v1/payments/webhook/",
        {
            "external_payment_id": "test_payment_failed",
            "status": "FAILED",
        },
        format="json",
    )

    assert response.status_code == 200

    payment.refresh_from_db()
    booking.refresh_from_db()

    assert payment.payment_status == PaymentStatus.FAILED
    assert booking.status == BookingStatus.PENDING
    
    
    
@pytest.mark.django_db   
def test_duplicate_payment_webhook_is_rejected():
    parent=Parent.objects.create(
        name="Duplicate Parent",
        email="duplicate@gmail.com"
    )
    lsa=LSAProfile.objects.create(
        name="Duplicate Test LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )
    booking=BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name="Duplicate Test Child",
        start_time="2026-08-20T14:00:00Z",
        end_time="2026-08-20T15:00:00Z",
        status=BookingStatus.PENDING,
    )
    Payment.objects.create(
        booking=booking,
        payment_status=PaymentStatus.PENDING,
        external_payment_id="test_duplicate_payment",
    )
    client=APIClient()
    first_response=client.post(
        "/api/v1/payments/webhook/",
        {
            "external_payment_id":"test_duplicate_payment",
            "status":"SUCCESS"
        },
        format="json"
    )
    assert first_response.status_code==200
    
    second_res=client.post(
        "/api/v1/payments/webhook/",
        {
            "external_payment_id": "test_duplicate_payment",
            "status": "SUCCESS",
        },
        format="json",
    )
    assert second_res.status_code==409
    