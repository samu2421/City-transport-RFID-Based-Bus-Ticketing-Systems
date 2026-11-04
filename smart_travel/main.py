from flask import Flask, render_template, redirect, url_for, flash, abort, request, session
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from functools import wraps
from smart_travel.forms import RegisterForm, LoginForm
import razorpay
import logging
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime as dt

########################################################################################################################
# CONFIGURATION
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

razor_key = os.environ.get("RAZOR_KEY")
razor_secret = os.environ.get("RAZOR_SECRET")

# Fare charged per kilometre travelled, in rupees.
FARE_PER_KM = 4
# The user with this id is the administrator (the first account in the database).
ADMIN_USER_ID = 1
# Replies understood by the ESP32 reader: it lights the green LED for SUCCESS and the red LED otherwise.
SUCCESS = "100"
FAILURE = "101"
TIMESTAMP_FORMAT = '%d/%m/%Y, %H:%M:%S'

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

########################################################################################################################
# INITIALIZATION
app = Flask(__name__, instance_path=str(PROJECT_ROOT / "instance"))
login_manager = LoginManager()
login_manager.login_view = "login"

app.config['SECRET_KEY'] = os.environ.get("APP_SECRET")
if not app.config['SECRET_KEY']:
    app.logger.warning("APP_SECRET is not set; using a temporary key, so sessions end when the server restarts.")
    app.config['SECRET_KEY'] = secrets.token_hex(32)

login_manager.init_app(app)
Bootstrap(app)


########################################################################################################################
# CONNECT TO DB
def get_database_uri():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        # Heroku-style URLs use the "postgres://" scheme, which SQLAlchemy no longer accepts.
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url
    os.makedirs(app.instance_path, exist_ok=True)
    return "sqlite:///" + os.path.join(app.instance_path, "travel.db")


app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    rfid = db.Column(db.String(250), nullable=True, unique=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    entries = relationship("Task", backref="passenger", cascade="all, delete-orphan")


class Task(db.Model):
    """A journey in progress: created on the first tap, completed on the second, removed once paid."""
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    uid_1 = db.Column(db.String(250), unique=True, nullable=True)
    dec_1 = db.Column(db.String(250), nullable=True)

    uid_2 = db.Column(db.String(250), nullable=True)
    dec_2 = db.Column(db.String(250), nullable=True)

    distance = db.Column(db.Float, nullable=True)
    due = db.Column(db.String(250), nullable=True)

    initial_timestamp = db.Column(db.String(250), nullable=True)
    final_timestamp = db.Column(db.String(250), nullable=True)


class Stations(db.Model):
    __tablename__ = "stations"
    id = db.Column(db.Integer, primary_key=True)
    station_name = db.Column(db.String(250), unique=True, nullable=False)
    # Stop code sent by the reader, e.g. "stop1".
    station_hexa = db.Column(db.String(250), unique=True, nullable=False)
    distance_from_initial = db.Column(db.Float, nullable=False)


class UserHistory(db.Model):
    __tablename__ = "user_history"
    id = db.Column(db.Integer, primary_key=True)
    card = db.Column(db.String(250), nullable=True)
    _from = db.Column(db.String(250), nullable=True)
    _to = db.Column(db.String(250), nullable=True)
    _from_time = db.Column(db.String(250), nullable=True)
    _to_time = db.Column(db.String(250), nullable=True)
    travel_distance = db.Column(db.Float, nullable=True)
    order_payment_id = db.Column(db.String(250), nullable=True)

    ticket_due = db.Column(db.Integer, nullable=True)


with app.app_context():
    db.create_all()


@app.cli.command("init-db")
def init_db_command():
    """Create the tables and load the stations and demo users from database/seed.sql (SQLite only)."""
    db.create_all()
    seed_sql = (PROJECT_ROOT / "database" / "seed.sql").read_text(encoding="utf-8")
    connection = db.engine.raw_connection()
    try:
        connection.driver_connection.executescript(seed_sql)
        connection.commit()
    finally:
        connection.close()
    print(f"Database ready: {app.config['SQLALCHEMY_DATABASE_URI']}")


@app.context_processor
def inject_admin_id():
    return {"admin_user_id": ADMIN_USER_ID}


########################################################################################################################
# FARE CALCULATION
def calculate_fare(start_km, end_km):
    """Return (distance in km, fare in rupees) between two stops given their distance from the first stop."""
    distance_travelled = abs(round(end_km - start_km, 2))
    ticket_cost = abs(round(distance_travelled * FARE_PER_KM, 0))
    return distance_travelled, ticket_cost


def get_razorpay_client():
    return razorpay.Client(auth=(razor_key, razor_secret))


########################################################################################################################
# ADMIN ONLY DECORATOR
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if current_user.id != ADMIN_USER_ID:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


########################################################################################################################

# USER LOADER
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


########################################################################################################################
# HOME ROUTE
@app.route('/')
def home():
    return render_template('index.html', current_user=current_user)


########################################################################################################################
# ADMIN_ONLY_ROUTE
@app.route('/admin', methods=["GET", "POST"])
@admin_only
def admin():
    all_users = User.query.all()
    return render_template("admin.html", current_user=current_user, all_users=all_users)


@app.route('/user_details')
@admin_only
def show_details():
    id_for_details = request.args.get("user_detail_id", type=int)
    selected_user = db.get_or_404(User, id_for_details)
    return render_template('admin_user.html', selected_user=selected_user)


# ADMIN_ONLY_DELETE_USER
@app.route('/admin/delete_user', methods=["GET", "POST"])
@admin_only
def delete_user():
    uid_to_delete = request.args.get('user_id_to_delete', type=int)
    user_to_delete = db.get_or_404(User, uid_to_delete)
    if user_to_delete.id == ADMIN_USER_ID:
        flash("The admin account cannot be removed.")
        return redirect(url_for("admin"))
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for("admin"))


# ADMIN_ONLY_ADD_USER_RFID
@app.route('/admin/add_rfid', methods=["POST"])
@admin_only
def add_user_rfid():
    new_user_id = request.args.get("user_id_for_rfid", type=int)
    new_user_rfid = db.get_or_404(User, new_user_id)
    rfid_value = request.form.get("rfid_value", "").strip()
    if not rfid_value:
        flash("Please enter the RFID number.")
        return redirect(url_for('show_details', user_detail_id=new_user_id))
    new_user_rfid.rfid = rfid_value
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash(f"RFID {rfid_value} is already assigned to another user.")
    return redirect(url_for('admin'))


########################################################################################################################


# REGISTER
@app.route('/register', methods=["GET", "POST"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        name = register_form.name.data
        email = register_form.email.data
        password = register_form.password.data

        if User.query.filter_by(email=email).first():
            flash(f"User with email {email} is already registered, Please Login.")
            return redirect(url_for('login'))
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=10)
            new_user = User(
                email=email,
                password=hashed_password,
                name=name,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=register_form, current_user=current_user)


# LOGIN
@app.route('/login', methods=["GET", "POST"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if not check_password_hash(user.password, password):
                flash("Incorrect password")
                return redirect(url_for('login'))
            else:
                login_user(user)
                return redirect(url_for('home'))
        else:
            flash("Please register.")
            return redirect(url_for('register'))
    return render_template('login.html', form=login_form, current_user=current_user)


# USER_PROFILE
@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    recent = UserHistory.query.filter_by(card=current_user.rfid).all() if current_user.rfid else []
    pending = Task.query.filter_by(passenger_id=current_user.id).first()
    return render_template("profile.html", current_user=current_user, recent=recent, pending=pending)


# ABOUT_US
@app.route('/about', methods=["GET", "POST"])
def about():
    return render_template('about.html', current_user=current_user)


# LOGOUT_USER
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# CARD TAP FROM THE ESP32 READER
# Request body: {"uid": " 77 208 30 43", "stp": "stop1"}. Reply: "100" (accepted) or "101" (rejected).
@app.route('/tryMy', methods=['POST'])
def get_json():
    val = request.get_json(silent=True)
    if not isinstance(val, dict) or not isinstance(val.get('uid'), str) or not isinstance(val.get('stp'), str):
        app.logger.warning("Rejected malformed tap request: %r", val)
        return FAILURE

    uid = val['uid'].strip()
    stop = val['stp'].strip()
    app.logger.info("Card tap: uid=%s stop=%s", uid, stop)

    passenger = User.query.filter_by(rfid=uid).first()
    if not passenger:
        app.logger.info("Card %s is not assigned to any user.", uid)
        return FAILURE

    station = Stations.query.filter_by(station_hexa=stop).first()
    if not station:
        app.logger.warning("Stop code %s is not in the stations table.", stop)
        return FAILURE

    entry = Task.query.filter_by(uid_1=uid).first()
    if not entry:
        # First tap: the passenger boards at this stop.
        first_entry = Task(
            uid_1=uid,
            dec_1=stop,
            passenger=passenger,
            initial_timestamp=dt.now().strftime(TIMESTAMP_FORMAT),
        )
        db.session.add(first_entry)
        db.session.commit()
        return SUCCESS

    if entry.due is not None:
        app.logger.info("Card %s has an unpaid fare of Rs.%s.", uid, entry.due)
        return FAILURE

    if entry.dec_1 == stop:
        app.logger.info("Card %s tapped out at its entry stop %s.", uid, stop)
        return FAILURE

    # Second tap at a different stop: the passenger leaves, so calculate the fare.
    start_station = Stations.query.filter_by(station_hexa=entry.dec_1).first()
    distance_travelled, ticket_cost = calculate_fare(start_station.distance_from_initial,
                                                     station.distance_from_initial)
    entry.uid_2 = uid
    entry.dec_2 = stop
    entry.final_timestamp = dt.now().strftime(TIMESTAMP_FORMAT)
    entry.distance = distance_travelled
    entry.due = ticket_cost
    db.session.commit()
    app.logger.info("User travelled from %s to %s: %s KM, Rs.%s.", start_station.station_name,
                    station.station_name, distance_travelled, ticket_cost)
    return SUCCESS


# PAYMENT: CREATE A RAZORPAY ORDER AND OPEN CHECKOUT
@app.route('/process_pay', methods=["POST"])
@login_required
def process_pay():
    user_payment = Task.query.filter_by(passenger_id=current_user.id).first()
    if not user_payment:
        flash("User do not have any pending transaction.")
        return redirect(url_for('profile'))
    if user_payment.due is None:
        flash("No due payments.")
        return redirect(url_for('profile'))
    if not (razor_key and razor_secret):
        flash("Online payment is not configured. Set RAZOR_KEY and RAZOR_SECRET in the .env file.")
        return redirect(url_for('profile'))

    amount_in_paise = int(round(float(user_payment.due) * 100))
    data = {"amount": amount_in_paise, "currency": "INR", "receipt": f"trip_{user_payment.id}"}
    try:
        order = get_razorpay_client().order.create(data=data)
    except Exception:
        app.logger.exception("Could not create a Razorpay order.")
        flash("The payment gateway could not be reached. Please try again.")
        return redirect(url_for('profile'))

    session['pending_order'] = {"order_id": order["id"], "task_id": user_payment.id}
    return render_template(
        'payment_checkout.html',
        order=order,
        trip=user_payment,
        razor_key=razor_key,
        start_station=Stations.query.filter_by(station_hexa=user_payment.dec_1).first().station_name,
        end_station=Stations.query.filter_by(station_hexa=user_payment.dec_2).first().station_name,
    )


# PAYMENT: VERIFY THE CHECKOUT RESULT AND SETTLE THE TRIP
@app.route('/payment/verify', methods=["POST"])
@login_required
def verify_payment():
    pending_order = session.get('pending_order')
    params = {
        "razorpay_order_id": request.form.get("razorpay_order_id", ""),
        "razorpay_payment_id": request.form.get("razorpay_payment_id", ""),
        "razorpay_signature": request.form.get("razorpay_signature", ""),
    }
    if not pending_order or pending_order["order_id"] != params["razorpay_order_id"]:
        flash("This payment does not match your pending fare.")
        return redirect(url_for('profile'))

    try:
        get_razorpay_client().utility.verify_payment_signature(params)
    except razorpay.errors.SignatureVerificationError:
        app.logger.warning("Payment signature check failed for order %s.", params["razorpay_order_id"])
        flash("Payment could not be verified.")
        return redirect(url_for('profile'))

    user_payment = db.session.get(Task, pending_order["task_id"])
    if not user_payment or user_payment.passenger_id != current_user.id:
        flash("User do not have any pending transaction.")
        return redirect(url_for('profile'))

    record_user_entry = UserHistory(
        card=user_payment.passenger.rfid,
        _from=Stations.query.filter_by(station_hexa=user_payment.dec_1).first().station_name,
        _to=Stations.query.filter_by(station_hexa=user_payment.dec_2).first().station_name,
        _from_time=user_payment.initial_timestamp,
        _to_time=user_payment.final_timestamp,
        travel_distance=user_payment.distance,
        ticket_due=int(float(user_payment.due)),
        order_payment_id=params["razorpay_order_id"],
    )
    db.session.add(record_user_entry)
    db.session.delete(user_payment)
    db.session.commit()
    session.pop('pending_order', None)

    payment = {
        "id": params["razorpay_order_id"],
        "payment_id": params["razorpay_payment_id"],
        "amount": record_user_entry.ticket_due * 100,
        "status": "paid",
    }
    return render_template('payment_receipt.html', payment=payment, _entry=record_user_entry)


if __name__ == "__main__":
    # Listen on all network interfaces so the ESP32 on the same Wi-Fi network can reach /tryMy.
    app.run(
        host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
