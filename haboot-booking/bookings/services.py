from .repositories import *
from django.db import transaction
from .models import *
from .exceptions import *


def search_lsas(*,skill,start_time,end_time):
    return find_available_lsas(
        skill=skill,
        start_time=start_time,
        end_time=end_time
    )
    
    
    
@transaction.atomic
def create_booking(*,parent_id,lsa_id,child_name,skill,start_time,end_time):
    parent=find_parent(parent_id)
    if parent is None:
        raise ParentNotFoundError("Parent not found")
    lsa=find_lsa_for_updates(lsa_id)
    if lsa is None:
        raise LSANotFoundError("LSA not found")
    if not lsa.is_active:
        raise LSANotActiveError("LSA is not active")
    if skill not in lsa.skills:
        raise SkillMisMatchError("Required skill is mismatched by LSA.")
    overlapping_count=count_overlapping_bookings(lsa=lsa,start_time=start_time,end_time=end_time)
    if overlapping_count>=lsa.max_concurrent_students:
        raise LSAUnavailableError("LSA no longer available  for requested time slot")
    booking=BookingRequest.objects.create(
        parent=parent,
        lsa=lsa,
        child_name=child_name,
        start_time=start_time,
        end_time=end_time,
        status=BookingStatus.PENDING
    )
    payment=Payment.objects.create(booking=booking)
    return booking


@transaction.atomic
def process_payment_webhook(*,external_payment_id,status):
    payment=(
        Payment.objects.select_for_update().filter(external_payment_id=external_payment_id).first()
    )
    if payment is None:
        raise PaymentNotFoundError("Payment not found")
    if payment.payment_status!=PaymentStatus.PENDING:
        raise InvalidPaymentTransactionError("Payment is already processed")
    if status==PaymentStatus.SUCCESS:
        payment.payment_status=PaymentStatus.SUCCESS
        payment.save(
            update_fields=[
                "payment_status",
                "updated_at"
            ]
        )
        booking=payment.booking
        booking.status=BookingStatus.CONFIRMED
        booking.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )
    elif status==PaymentStatus.FAILED:
        payment.payment_status = PaymentStatus.FAILED
        payment.save(
            update_fields=[
                "payment_status",
                "updated_at",
            ]
        )
    return payment
