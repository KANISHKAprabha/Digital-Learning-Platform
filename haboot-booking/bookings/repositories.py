from django.db import models
from django.db.models import Count ,Q


from .models import *

def find_available_lsas(skill,start_time,end_time):
    overlapping_filter=Q(
        bookings__status__in=[
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED
        ],
        bookings__start_time__lt=end_time,
        bookings__end_time__gt=start_time
    )
    return (
        LSAProfile.objects.filter(
            is_active=True,
            skills__contains=[skill]
        ).annotate(
            overlapping_bookings=Count(
                "bookings",
                filter=overlapping_filter,
            )
        ).filter(
            overlapping_bookings__lt=models.F("max_concurrent_students")
        ).order_by("-max_concurrent_students")
    )
    
    
def find_parent(parent_id):
    return Parent.objects.filter(id=parent_id).first()


def find_lsa(lsa_id):
    return LSAProfile.objects.filter(id=lsa_id).first()


def find_overlapping_bookings(lsa,start_time,end_time):
    return BookingRequest.objects.filter(
        lsa=lsa,
        status__in=[
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED
        ],
        start_time__lt=end_time,
        end_time__gt=start_time
    )

def count_overlapping_bookings(lsa,start_time,end_time):
    return find_overlapping_bookings(
        lsa=lsa,
        start_time=start_time,
        end_time=end_time
    ).count()


def find_lsa_for_updates(lsa_id):
    return LSAProfile.objects.select_for_update().filter(id=lsa_id).first()

