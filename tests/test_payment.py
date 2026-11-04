"""Payment flow with the Razorpay client mocked out (no network calls, no real money)."""
from unittest import mock

import razorpay

from smart_travel import main
from smart_travel.main import Task, UserHistory
from tests.conftest import PASSENGER_CARD, log_in, tap


def finish_trip(client):
    log_in(client, "passenger@test.local", "passenger123")
    tap(client, PASSENGER_CARD, "stop2")
    tap(client, PASSENGER_CARD, "stop3")   # 3.3 km -> Rs. 13


def fake_client(order_id="order_TEST123", signature_ok=True):
    client = mock.Mock()
    client.order.create.return_value = {"id": order_id, "amount": 1300, "currency": "INR", "status": "created"}
    if not signature_ok:
        client.utility.verify_payment_signature.side_effect = razorpay.errors.SignatureVerificationError("bad")
    return client


def test_pay_without_keys_shows_message(client):
    finish_trip(client)
    response = client.post("/process_pay", follow_redirects=True)
    assert b"Online payment is not configured" in response.data
    assert Task.query.count() == 1


def test_pay_with_no_trip(client, payment_keys):
    log_in(client, "passenger@test.local", "passenger123")
    response = client.post("/process_pay", follow_redirects=True)
    assert b"do not have any pending transaction" in response.data


def test_pay_during_journey(client, payment_keys):
    log_in(client, "passenger@test.local", "passenger123")
    tap(client, PASSENGER_CARD, "stop1")
    response = client.post("/process_pay", follow_redirects=True)
    assert b"No due payments" in response.data


def test_checkout_creates_order_in_paise(client, payment_keys):
    finish_trip(client)
    razor = fake_client()
    with mock.patch.object(main, "get_razorpay_client", return_value=razor):
        response = client.post("/process_pay")
    assert response.status_code == 200
    razor.order.create.assert_called_once()
    data = razor.order.create.call_args.kwargs["data"]
    assert data["amount"] == 1300 and isinstance(data["amount"], int)
    assert data["currency"] == "INR"
    assert b"order_TEST123" in response.data and b"checkout.razorpay.com" in response.data
    # Nothing is settled until the payment is verified.
    assert Task.query.count() == 1 and UserHistory.query.count() == 0


def test_verified_payment_settles_trip(client, payment_keys):
    finish_trip(client)
    razor = fake_client()
    with mock.patch.object(main, "get_razorpay_client", return_value=razor):
        client.post("/process_pay")
        response = client.post("/payment/verify", data={
            "razorpay_order_id": "order_TEST123",
            "razorpay_payment_id": "pay_TEST456",
            "razorpay_signature": "sig",
        })
    assert response.status_code == 200
    assert b"pay_TEST456" in response.data and b"13.0 Rs." in response.data
    history = UserHistory.query.one()
    assert (history._from, history._to, history.ticket_due) == ("Anand Nagar", "Deccan", 13)
    assert history.card == PASSENGER_CARD and history.order_payment_id == "order_TEST123"
    assert Task.query.count() == 0
    # The card can start a new journey.
    assert tap(client, PASSENGER_CARD, "stop1") == "100"


def test_bad_signature_does_not_settle(client, payment_keys):
    finish_trip(client)
    with mock.patch.object(main, "get_razorpay_client", return_value=fake_client(signature_ok=False)):
        client.post("/process_pay")
        response = client.post("/payment/verify", data={
            "razorpay_order_id": "order_TEST123", "razorpay_payment_id": "pay_X", "razorpay_signature": "bad",
        }, follow_redirects=True)
    assert b"could not be verified" in response.data
    assert Task.query.count() == 1 and UserHistory.query.count() == 0


def test_mismatched_order_does_not_settle(client, payment_keys):
    finish_trip(client)
    with mock.patch.object(main, "get_razorpay_client", return_value=fake_client()):
        client.post("/process_pay")
        response = client.post("/payment/verify", data={
            "razorpay_order_id": "order_OTHER", "razorpay_payment_id": "pay_X", "razorpay_signature": "sig",
        }, follow_redirects=True)
    assert b"does not match" in response.data
    assert Task.query.count() == 1


def test_gateway_error_is_reported(client, payment_keys):
    finish_trip(client)
    razor = fake_client()
    razor.order.create.side_effect = ConnectionError("offline")
    with mock.patch.object(main, "get_razorpay_client", return_value=razor):
        response = client.post("/process_pay", follow_redirects=True)
    assert b"could not be reached" in response.data
