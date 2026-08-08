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