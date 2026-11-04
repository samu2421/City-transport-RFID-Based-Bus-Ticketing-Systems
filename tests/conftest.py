import os
import tempfile

import pytest

# The app reads its configuration when the module is imported, so point it at a throwaway database
# and clear the payment keys before importing it.
_db_dir = tempfile.mkdtemp(prefix="smart_travel_tests_")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_db_dir, "test.db")
os.environ["APP_SECRET"] = "test-secret"
os.environ.pop("RAZOR_KEY", None)
os.environ.pop("RAZOR_SECRET", None)

from werkzeug.security import generate_password_hash  # noqa: E402

from smart_travel import main  # noqa: E402
from smart_travel.main import app, db, Stations, User  # noqa: E402

ADMIN_CARD = "77 208 30 43"
PASSENGER_CARD = "108 145 014 59"


@pytest.fixture
def client():
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add_all([
            Stations(id=1, station_name="Kothrud Depot", station_hexa="stop1", distance_from_initial=0.0),
            Stations(id=2, station_name="Anand Nagar", station_hexa="stop2", distance_from_initial=2.7),
            Stations(id=3, station_name="Deccan", station_hexa="stop3", distance_from_initial=6.0),
            Stations(id=4, station_name="Ma Na Pa", station_hexa="stop4", distance_from_initial=9.3),
            User(id=1, rfid=ADMIN_CARD, name="Admin", email="admin@test.local",
                 password=generate_password_hash("admin123")),
            User(id=2, rfid=PASSENGER_CARD, name="Passenger", email="passenger@test.local",
                 password=generate_password_hash("passenger123")),
            User(id=3, rfid=None, name="No Card", email="nocard@test.local",
                 password=generate_password_hash("nocard123")),
        ])
        db.session.commit()
        yield app.test_client()
        db.session.remove()


@pytest.fixture
def payment_keys(monkeypatch):
    monkeypatch.setattr(main, "razor_key", "rzp_test_dummy")
    monkeypatch.setattr(main, "razor_secret", "dummy_secret")


def tap(client, uid, stop):
    """Send a card tap exactly as the ESP32 firmware does and return the reply text."""
    return client.post("/tryMy", json={"uid": uid, "stp": stop}).get_data(as_text=True)


def log_in(client, email, password):
    return client.post("/login", data={"email": email, "password": password})
