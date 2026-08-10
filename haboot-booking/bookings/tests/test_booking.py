

import pytest
from rest_framework.test import APIClient

from bookings.models import *

@pytest.mark.django_db

def test_successful_booking_creates_booking_and_payment(monkeypatch):
    def fake_payment_request(*args,**kwargs):
        class FakeResponse:
            def raise_for_status(self):
                pass
            def json(self):
                return {
                    "success":True,
                    "external_payment_id":"test_payment_id",
                    "status":"PENDING"
                    
                }
        return FakeResponse()
    monkeypatch.setattr("bookings.payment_services.requests.post",fake_payment_request)
    parent=Parent.objects.create(name="Test Parent",email="testparent@gmail.com")
    lsa=LSAProfile.objects.create(name="Test LSA",skills=["dyslexia"],qualification="Special Eduction",experience_years=5,max_concurrent_students=4,is_active=True)
    client=APIClient()
    response=client.post(
        "/api/v1/bookings/",
        {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Test Child",
            "skill": "dyslexia",
            "start_time": "2026-08-20T10:00:00Z",
            "end_time": "2026-08-20T11:00:00Z",
        },
        format="json",
    )
    assert response.status_code==201
    booking=BookingRequest.objects.get(
        id=response.data["booking_id"]
    )
    assert booking.status==BookingStatus.PENDING
    payment=Payment.objects.get(booking=booking)
    assert payment.payment_status==PaymentStatus.PENDING
    
    
    
    
    
@pytest.mark.django_db
def test_booking_rejected_when_lsa_capacity_is_full():
    parent=Parent.objects.create(name="Test Parent",email="capacity@example.com")
    lsa = LSAProfile.objects.create(
        name="Capacity Test LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=2,
        is_active=True,
    )
    BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name="Child One",
        start_time="2026-08-20T10:00:00Z",
        end_time="2026-08-20T11:00:00Z",
        status=BookingStatus.CONFIRMED,
    )

    BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name="Child Two",
        start_time="2026-08-20T10:30:00Z",
        end_time="2026-08-20T11:30:00Z",
        status=BookingStatus.PENDING,
    )
    client=APIClient()
    response=client.post(
        "/api/v1/bookings/",
        {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Child Three",
            "skill": "dyslexia",
            "start_time": "2026-08-20T10:15:00Z",
            "end_time": "2026-08-20T10:45:00Z", 
        },
        format="json"
        
    )
    assert response.status_code==409
    assert response.data["error"]==(
        "LSA no longer available  for requested time slot"
    )
    
    
@pytest.mark.django_db
def test_booking_rejected_when_skill_does_not_match():

    parent = Parent.objects.create(
        name="Test Parent",
        email="skill@example.com",
    )

    lsa = LSAProfile.objects.create(
        name="Skill Test LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )

    client = APIClient()

    response = client.post(
        "/api/v1/bookings/",
        {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Skill Test Child",
            "skill": "autism",
            "start_time": "2026-08-20T14:00:00Z",
            "end_time": "2026-08-20T15:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400

    assert response.data["error"] == (
        "Required skill is mismatched by LSA."
    )
    
    
    
    
@pytest.mark.django_db
def test_booking_rejected_when_end_time_is_before_start_time():

    parent = Parent.objects.create(
        name="Test Parent",
        email="time@example.com",
    )

    lsa = LSAProfile.objects.create(
        name="Time Test LSA",
        skills=["dyslexia"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )

    client = APIClient()

    response = client.post(
        "/api/v1/bookings/",
        {
            "parent_id": parent.id,
            "lsa_id": lsa.id,
            "child_name": "Time Test Child",
            "skill": "dyslexia",
            "start_time": "2026-08-20T17:00:00Z",
            "end_time": "2026-08-20T16:00:00Z",
        },
        format="json",
    )

    assert response.status_code == 400
    print(response.data)

    assert response.data["non_field_errors"][0] == (
    "start_time must be before end_time."
)