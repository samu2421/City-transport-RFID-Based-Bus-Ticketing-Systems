-- Smart Travel database schema (SQLite).
-- Exported from the original project database (Travel.db, 2022). The Flask app creates the same
-- tables automatically through SQLAlchemy (db.create_all()), so this file is a reference and an
-- alternative way to build the database by hand:
--     sqlite3 instance/travel.db < database/schema.sql

CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL,
    rfid VARCHAR(250),
    name VARCHAR(250) NOT NULL,
    email VARCHAR(250) NOT NULL,
    password VARCHAR(250) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (rfid),
    UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS stations (
    id INTEGER NOT NULL,
    station_name VARCHAR(250) NOT NULL,
    station_hexa VARCHAR(250) NOT NULL,
    distance_from_initial FLOAT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (station_name),
    UNIQUE (station_hexa)
);

CREATE TABLE IF NOT EXISTS user_history (
    id INTEGER NOT NULL,
    card VARCHAR(250),
    _from VARCHAR(250),
    _to VARCHAR(250),
    _from_time VARCHAR(250),
    _to_time VARCHAR(250),
    travel_distance FLOAT,
    order_payment_id VARCHAR(250),
    ticket_due INTEGER,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER NOT NULL,
    passenger_id INTEGER,
    uid_1 VARCHAR(250),
    dec_1 VARCHAR(250),
    uid_2 VARCHAR(250),
    dec_2 VARCHAR(250),
    distance FLOAT,
    due VARCHAR(250),
    initial_timestamp VARCHAR(250),
    final_timestamp VARCHAR(250),
    PRIMARY KEY (id),
    FOREIGN KEY(passenger_id) REFERENCES users (id),
    UNIQUE (uid_1)
);
