-- Smart Travel seed data (SQLite). Loaded by:  flask --app smart_travel.main init-db
-- Safe to run more than once: existing rows are left unchanged.

-- Route used in the 2022 demonstration (Pune, PMPML). station_hexa is the stop code sent by the
-- ESP32 reader; distance_from_initial is the distance in km from the first stop.
INSERT OR IGNORE INTO stations (id, station_name, station_hexa, distance_from_initial) VALUES
    (1, 'Kothrud Depot', 'stop1', 0.0),
    (2, 'Anand Nagar',   'stop2', 2.7),
    (3, 'Deccan',        'stop3', 6.0),
    (4, 'Ma Na Pa',      'stop4', 9.3);

-- Demo accounts for local testing only. Change or remove them before any real use.
--   id 1 is the administrator:  admin@smarttravel.local     / admin123
--   id 2 is a passenger:        passenger@smarttravel.local / passenger123
-- The RFID values are the UIDs of the two cards used with the original hardware, in the format the
-- firmware sends (decimal bytes separated by spaces).
INSERT OR IGNORE INTO users (id, rfid, name, email, password) VALUES
    (1, '77 208 30 43', 'Demo Admin', 'admin@smarttravel.local',
     'pbkdf2:sha256:1000000$RH5fk9sZ4N$4f3ea6477f86e9d7de7b32449b77e1bfac0f5973278ab51806d1475f47983c4c'),
    (2, '108 145 014 59', 'Demo Passenger', 'passenger@smarttravel.local',
     'pbkdf2:sha256:1000000$yXuRYDBpOL$0d08a5a48b1c2d649add112c50191233b1088211ea727b8f37656242721b6ce2');
