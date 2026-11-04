"""Card tap handling at /tryMy, using the same JSON the ESP32 firmware sends (simulated hardware)."""
import pytest

from smart_travel.main import calculate_fare, db, Task
from tests.conftest import PASSENGER_CARD, tap


@pytest.mark.parametrize("start_km, end_km, distance, fare", [
    (0.0, 6.0, 6.0, 24.0),    # Kothrud Depot -> Deccan
    (2.7, 6.0, 3.3, 13.0),    # Anand Nagar -> Deccan (13.2 rounds to 13)
    (0.0, 9.3, 9.3, 37.0),    # Kothrud Depot -> Ma Na Pa (37.2 rounds to 37)
    (9.3, 2.7, 6.6, 26.0),    # travelling back towards the first stop
])
def test_calculate_fare(start_km, end_km, distance, fare):
    assert calculate_fare(start_km, end_km) == (distance, fare)


def test_entry_then_exit_records_fare(client):
    # The firmware prefixes the UID with a space; the server must strip it.
    assert tap(client, " " + PASSENGER_CARD, "stop1") == "100"
    assert tap(client, " " + PASSENGER_CARD, "stop3") == "100"
    trip = Task.query.filter_by(uid_1=PASSENGER_CARD).one()
    assert (trip.dec_1, trip.dec_2) == ("stop1", "stop3")
    assert trip.distance == 6.0
    assert float(trip.due) == 24.0
    assert trip.initial_timestamp and trip.final_timestamp


def test_unregistered_card_is_rejected(client):
    assert tap(client, "1 2 3 4", "stop1") == "101"
    assert Task.query.count() == 0


def test_exit_at_entry_stop_is_rejected(client):
    assert tap(client, PASSENGER_CARD, "stop2") == "100"
    assert tap(client, PASSENGER_CARD, "stop2") == "101"
    assert Task.query.one().due is None


def test_new_journey_blocked_until_fare_paid(client):
    tap(client, PASSENGER_CARD, "stop1")
    tap(client, PASSENGER_CARD, "stop2")
    assert tap(client, PASSENGER_CARD, "stop3") == "101"
    assert Task.query.one().dec_2 == "stop2"


def test_unknown_stop_is_rejected_without_changing_trip(client):
    assert tap(client, PASSENGER_CARD, "stop9") == "101"
    assert Task.query.count() == 0
    tap(client, PASSENGER_CARD, "stop1")
    assert tap(client, PASSENGER_CARD, "stop9") == "101"
    trip = Task.query.one()
    assert trip.dec_2 is None and trip.due is None


@pytest.mark.parametrize("body", [None, {}, {"uid": PASSENGER_CARD}, {"uid": 5, "stp": "stop1"}, ["x"]])
def test_malformed_requests_are_rejected(client, body):
    response = client.post("/tryMy", json=body) if body is not None else client.post("/tryMy", data="not json")
    assert response.status_code == 200
    assert response.get_data(as_text=True) == "101"


def test_get_request_not_allowed(client):
    assert client.get("/tryMy").status_code == 405


def test_deleting_user_removes_open_journey(client):
    tap(client, PASSENGER_CARD, "stop1")
    with client.application.app_context():
        from smart_travel.main import User
        db.session.delete(db.session.get(User, 2))
        db.session.commit()
    assert Task.query.count() == 0
