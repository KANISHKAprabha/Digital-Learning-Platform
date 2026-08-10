import pytest
from rest_framework.test import APIClient

from bookings.models import *


@pytest.mark.django_db
def test_lsa_search_filters_by_skill():

    LSAProfile.objects.create(
        name="Alice",
        skills=["dyslexia", "adhd"],
        qualification="Special Education",
        experience_years=5,
        max_concurrent_students=4,
        is_active=True,
    )

    LSAProfile.objects.create(
        name="David",
        skills=["speech"],
        qualification="Speech Therapy",
        experience_years=3,
        max_concurrent_students=4,
        is_active=True,
    )

    client = APIClient()

    response = client.get(
        "/api/v1/lsas/search/",
        {
            "skill": "dyslexia",
            "start_time": "2026-08-20T10:00:00Z",
            "end_time": "2026-08-20T11:00:00Z",
        },
    )

    assert response.status_code == 200

    assert len(response.data) == 1

    assert response.data[0]["name"] == "Alice"
    
    
    
    
@pytest.mark.django_db
def test_lsa_search_excludes_lsa_when_capacity_is_full():

    parent = Parent.objects.create(
        name="Search Parent",
        email="searchcapacity@example.com",
    )

    lsa = LSAProfile.objects.create(
        name="Full Capacity LSA",
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

    client = APIClient()

    response = client.get(
        "/api/v1/lsas/search/",
        {
            "skill": "dyslexia",
            "start_time": "2026-08-20T10:15:00Z",
            "end_time": "2026-08-20T10:45:00Z",
        },
    )

    assert response.status_code == 200

    assert len(response.data) == 0