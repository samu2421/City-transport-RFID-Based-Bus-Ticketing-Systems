"""Web pages, accounts and the admin panel."""
import pytest

from smart_travel.main import db, User
from tests.conftest import log_in, tap, PASSENGER_CARD


@pytest.mark.parametrize("path", ["/", "/about", "/login", "/register"])
def test_public_pages_render(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert b"Smart Travel" in response.data


def test_static_assets_are_served(client):
    for path in ["/static/assets/css/style.css", "/static/assets/js/main.js",
                 "/static/assets/img/logo-32x32.png", "/static/assets/vendor/bootstrap-icons/bootstrap-icons.css",
                 "/static/assets/vendor/bootstrap/css/bootstrap.min.css"]:
        with client.get(path) as response:
            assert response.status_code == 200, path


def test_register_logs_in_new_user(client):
    response = client.post("/register", data={"name": "New", "email": "new@test.local", "password": "pw"})
    assert response.status_code == 302
    assert client.get("/profile").status_code == 200
    user = User.query.filter_by(email="new@test.local").one()
    assert user.password != "pw"


def test_register_existing_email_redirects_to_login(client):
    response = client.post("/register", data={"name": "X", "email": "passenger@test.local", "password": "pw"})
    assert response.location.endswith("/login")


def test_login_wrong_password(client):
    response = log_in(client, "passenger@test.local", "wrong")
    assert response.location.endswith("/login")
    assert client.get("/profile").status_code == 302


def test_profile_shows_outstanding_fare_and_history(client):
    log_in(client, "passenger@test.local", "passenger123")
    tap(client, PASSENGER_CARD, "stop1")
    tap(client, PASSENGER_CARD, "stop3")
    page = client.get("/profile").data
    assert b"Outstanding fare: <strong>24 Rs.</strong>" in page
    assert PASSENGER_CARD.encode() in page


def test_profile_requires_login(client):
    response = client.get("/profile")
    assert response.status_code == 302 and "/login" in response.location


def test_admin_requires_login(client):
    response = client.get("/admin")
    assert response.status_code == 302 and "/login" in response.location


def test_admin_forbidden_for_passenger(client):
    log_in(client, "passenger@test.local", "passenger123")
    assert client.get("/admin").status_code == 403


def test_admin_lists_users_and_details(client):
    log_in(client, "admin@test.local", "admin123")
    page = client.get("/admin").data
    assert b"passenger@test.local" in page and b"RFID not assigned" in page
    assert client.get("/user_details?user_detail_id=3").status_code == 200
    assert client.get("/user_details?user_detail_id=99").status_code == 404


def test_admin_assigns_rfid(client):
    log_in(client, "admin@test.local", "admin123")
    client.post("/admin/add_rfid?user_id_for_rfid=3", data={"rfid_value": "  1 2 3 4 "})
    assert db.session.get(User, 3).rfid == "1 2 3 4"
    assert tap(client, " 1 2 3 4", "stop1") == "100"


def test_admin_cannot_assign_duplicate_rfid(client):
    log_in(client, "admin@test.local", "admin123")
    response = client.post("/admin/add_rfid?user_id_for_rfid=3", data={"rfid_value": PASSENGER_CARD},
                           follow_redirects=True)
    assert b"already assigned" in response.data
    assert db.session.get(User, 3).rfid is None


def test_admin_deletes_user_but_not_admin(client):
    log_in(client, "admin@test.local", "admin123")
    client.get("/admin/delete_user?user_id_to_delete=3")
    assert db.session.get(User, 3) is None
    response = client.get("/admin/delete_user?user_id_to_delete=1", follow_redirects=True)
    assert b"cannot be removed" in response.data
    assert db.session.get(User, 1) is not None


def test_logout(client):
    log_in(client, "passenger@test.local", "passenger123")
    client.get("/logout")
    assert client.get("/profile").status_code == 302
