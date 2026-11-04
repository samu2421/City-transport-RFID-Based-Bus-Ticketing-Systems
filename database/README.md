# Database

Smart Travel uses SQLite through Flask-SQLAlchemy. By default the database file is `instance/travel.db`,
which is created on first start and is not tracked by git.

| File | Purpose |
|---|---|
| [`schema.sql`](schema.sql) | Table definitions, exported from the original 2022 database |
| [`seed.sql`](seed.sql) | The four stations of the demonstration route and two demo accounts |

## Create the database

```bash
flask --app smart_travel.main init-db
```

This creates the tables (if needed) and loads `seed.sql`. It can be run again safely; existing rows are
kept. To build the database by hand instead:

```bash
mkdir -p instance
sqlite3 instance/travel.db < database/schema.sql
sqlite3 instance/travel.db < database/seed.sql
```

To start again from scratch, delete `instance/travel.db` and run `init-db` again.

## Tables

| Table | Contents |
|---|---|
| `users` | Accounts: name, email, hashed password and the assigned RFID card (`rfid`, unique). User id 1 is the administrator. |
| `stations` | Stops on the route: name, stop code sent by the reader (`station_hexa`, e.g. `stop1`) and distance in km from the first stop. |
| `tasks` | Journeys in progress. A row is created on the first tap, completed on the second tap (exit stop, distance, fare in `due`) and deleted once the fare is paid. |
| `user_history` | Completed, paid journeys: card, stop names, times, distance, fare and the Razorpay order id. |

The column names (`station_hexa`, `dec_1`, `dec_2`, `uid_1`, `uid_2`) are kept from the original project so
that existing databases still work.

## Adding stops

Add a row to `stations` with a new stop code and its distance from the first stop, for example:

```sql
INSERT INTO stations (station_name, station_hexa, distance_from_initial) VALUES ('Shivaji Nagar', 'stop5', 11.0);
```

A reader must send the same stop code. The current firmware has three readers (`stop1` to `stop3`), so
`stop4` in the seed data can only be reached with the reader simulator.
