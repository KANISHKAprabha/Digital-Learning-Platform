import requests


class PaymentServiceError(Exception):
   pass




def create_payment(*,booking_id,amount):
    try:
        response=requests.post(
            "http://127.0.0.1:8000/api/v1/mock-payments/",
            json={
                "booking_id":booking_id,
                "amount":amount
            },timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PaymentServiceError(
            "Payment service is unavailable"
        ) from exc
    data=response.json()
    return {
            "external_payment_id":f"mock_pay_{booking_id}",
            "status":data["status"]
        }