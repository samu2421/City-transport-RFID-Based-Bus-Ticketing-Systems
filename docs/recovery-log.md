# Recovery log

Record of how this repository was recovered and restructured in November 2026. "Original" paths are
relative to the recovered project folder as it was before the restructuring.

## 1. Starting point

The recovered folder contained one Flask application and one ESP32 sketch, stored several times over:

| Original path | What it was |
|---|---|
| `codes/Smart_Travel_code_files/SmartTravel_main_code/` | Flask app: the GitHub commit plus uncommitted fixes from Aug–Sep 2022 (newest version) |
| `train_ticket_scan-pay_system-master 2/` | Flask app as committed to GitHub (`aditya-ladawa/SmartTravel`, June 2022) |
| `codes/trying_code/trying_code.ino` | ESP32 firmware (the only copy apart from `Hardware.rar`) |
| `codes/*.rar`, `codes/Smart_Travel_code_files/**/*.rar` (6 archives) | Byte-identical backups of the folders above (checked by SHA-1 of every source file) |
| Root PDFs, `.pptx`, screenshots, `README.md` | Report, synopsis, early concept note, setup slides, demo screenshots, an earlier README |

Differences between the two app versions: the newer one strips spaces from card UIDs (required, because the
firmware sends a leading space), uses one date format for both journey timestamps, hard-codes SQLite and
adds "KM" on the profile page. The newer version was used as the base, with the GitHub version's
`DATABASE_URL` setting restored.

## 2. Backup

- Full archive before any change: `SmartTravel_backups/SmartTravel_original_2026-11-02.tar` (910 files,
  264 MB), stored next to the project folder, outside the repository.
- SHA-256 stored alongside it. The archive was extracted to a temporary folder and compared with the
  original using `diff -r`: identical.
- In addition, every original file was moved unchanged to `SmartTravel_review/original_layout/` outside the
  repository. Nothing was deleted.

## 3. Migration map

| Original path | New path | Action | Reason |
|---|---|---|---|
| `…/SmartTravel_main_code/.git/` | Private backup only | Kept privately | Used during the restructuring, then replaced by a fresh history (section 6) |
| `…/SmartTravel_main_code/main.py`, `forms.py` | `smart_travel/main.py`, `smart_travel/forms.py` | Copied, then fixed (section 5) | Application package |
| `…/templates/index.html`, `header.html`, `footer.html`, `admin.html` | `smart_travel/templates/` (same names) | Copied, then edited | Pages in use |
| `…/templates/about_us.html` | `smart_travel/templates/about.html` | Copied, renamed, rewritten | Consistent names; placeholder content replaced |
| `…/templates/LOGIN.html`, `REGISTER.html`, `PROFILE.html` | `login.html`, `register.html`, `profile.html` | Copied, renamed | Lowercase names |
| `…/templates/admin_profile.html` | `admin_user.html` | Copied, renamed | Describes what it shows (one user, for the admin) |
| `…/templates/successful_payment.html` | `payment_receipt.html` | Copied, renamed | Paired with the new `payment_checkout.html` |
| `…/static/assets/css`, `js`, `vendor` | `smart_travel/static/assets/…` | Copied | Used by the pages (except `vendor/php-email-form`, see section 4) |
| `…/static/assets/img/Logo 32x32.png` | `smart_travel/static/assets/img/logo-32x32.png` | Copied, renamed | No spaces in file names |
| `…/static/assets/img/` (6 images that are referenced) | `smart_travel/static/assets/img/` | Copied | Referenced by templates or CSS |
| `…/static/assets/img/pixelot_bus_1.jpg` (unused in the original) | `smart_travel/static/assets/img/city-buses.jpg` | Copied, resized | Replaces the template's stock photo (`about.jpg`) on the About page |
| `codes/trying_code/trying_code.ino` | `hardware/smart_travel_reader/smart_travel_reader.ino` | Copied, renamed, edited | The Arduino IDE needs the folder and sketch to share a name |
| 4 project screenshots (`Screenshot 2025-10-02 …`) | `docs/screenshots/demo-model.jpg`, `home-page.jpg`, `admin-dashboard.jpg`, `user-profile.jpg` | Copied, resized to 1400 px, JPEG | Descriptive names; 8.9 MB reduced to 0.5 MB |
| `train_ticket…/Travel.db` (schema) | `database/schema.sql` | Exported (read-only) | Schema as SQL instead of a binary database |
| Missing `table.py` (station seeding script, lost) | `database/seed.sql` + `flask init-db` | Recreated | The stations table must be filled for fares to work |

## 4. Not included in the repository

All of these remain in `SmartTravel_review/original_layout/` and in the backup archive.

| Item | Reason |
|---|---|
| 6 RAR archives, `train_ticket_scan-pay_system-master 2/` | Duplicates of the code that was migrated |
| Both `Travel.db` files | Contain teammates' real email addresses and password hashes; replaced by `schema.sql` and `seed.sql` |
| `.env` | Contains a Flask secret, Razorpay test keys and a Heroku database URL with credentials; replaced by `.env.example` |
| `Instructions(READ ME).txt` | Contains a teammate's email and a plaintext password |
| `smart travel working steps.pptx` | Slide 14 contains the same login; the setup steps are now in this README |
| `Final report.pdf`, `PBL Synopsis.pdf` | Contain the team's university seat numbers; can be added later if the team agrees |
| `Automated payment system for buses.pdf` | Early concept (fingerprint scanner, wallet) that was not built |
| `Screenshot 2025-10-03 at 22.38.57.png` | Unrelated to the project (personal browser screenshot) |
| Original `README.md` (2024) | Rewritten; it described features the code does not have |
| `Extras.html`, `login_form.html`, `register_form.html`, `static/form_assets/`, `static/log_reg_assets/` | Unused template pages and their assets |
| `static/assets/css/admin_profile.css`, `static/assets/my_pay_script/pay_script.js` | Not linked from any page; the payment script is replaced by `payment_checkout.html` |
| `forms/contact.php`, `static/assets/vendor/php-email-form/` | PHP contact form from the website template; never runs under Flask |
| Unreferenced images (`portfolio/`, `clients/`, `testimonials/`, others), `img.zip`, `favicon_io.zip` | Not used by any page |
| Unused vendor builds: Bootstrap source maps, RTL/ESM/grid/reboot/utilities builds, unminified copies of minified files | No page loads them; the vendor folder went from 14 MB to 5.2 MB |
| `static/assets/vendor/isotope-layout/` and its `<script>` tag in `footer.html` | Only used by the template's portfolio grid, which no page contains (the code in `main.js` runs only if a `.portfolio-container` element exists); it was also the only GPL-licensed file |
| `Procfile` | Pointed to `main:application`, which never existed; the Heroku deployment is no longer available |
| `requirements.txt` (UTF-16, about 80 packages) | Replaced; it listed a whole Jupyter environment and missed Flask-Login and Flask-SQLAlchemy |
| `.idea/`, `__pycache__/`, `.DS_Store`, old `.gitignore` | IDE, cache and OS files |

## 5. Changes to the code

| Problem | Change | Files | Verified by |
|---|---|---|---|
| App could not start: `wtforms.fields.html5` was removed in WTForms 3 | Import `EmailField` from `wtforms`; removed two unused forms | `forms.py` | All tests |
| App could not start: `db.create_all()` outside an app context (Flask-SQLAlchemy 3) | Run inside `app.app_context()` | `main.py` | All tests |
| App could not start: `app.run(host='copy_paste_ipv4')` placeholder | Listen on `0.0.0.0:5000` by default, configurable through the environment | `main.py` | End-to-end run |
| Razorpay keys read before `.env` was loaded | Load `.env` first | `main.py` | Payment tests |
| No way to fill the stations table (`table.py` lost) | `flask init-db` command and `database/seed.sql` | `main.py`, `database/` | Run twice on an empty database |
| Payment checkout never opened (`pay_script.js` had template code in a static file) and trips were marked paid as soon as an order was created | Checkout page with Razorpay Checkout; new `/payment/verify` checks the signature before saving the trip to history | `main.py`, `payment_checkout.html`, `payment_receipt.html`, `profile.html` | `test_payment.py` (mocked Razorpay) |
| Any logged-in user could settle another user's fare (`?user_id_for_payment=`) | Use the logged-in user | `main.py`, `profile.html` | `test_payment.py` |
| Razorpay amount sent as a float | Integer amount in paise | `main.py` | `test_checkout_creates_order_in_paise` |
| Admin pages crashed (500) for logged-out visitors | Redirect to the login page | `main.py` | `test_admin_requires_login` |
| `/tryMy` crashed on malformed JSON or an unknown stop, and an unknown stop left a half-updated journey | Validate input and stops before writing; reply `101` | `main.py` | `test_tap_flow.py` |
| Assigning a card that another user already has crashed; GET on `/admin/add_rfid` crashed | Friendly message; POST only | `main.py` | `test_admin_cannot_assign_duplicate_rfid` |
| The admin account could be deleted (the original setup slides say it cannot) | Blocked, and the button is hidden for the admin | `main.py`, `admin_user.html` | `test_admin_deletes_user_but_not_admin` |
| Deleting a user left their open journey behind | Delete it with the user | `main.py` | `test_deleting_user_removes_open_journey` |
| Profile loaded every user's history and never showed the amount owed | Query by card; show the outstanding fare | `main.py`, `profile.html` | `test_profile_shows_outstanding_fare_and_history` |
| Relative `static/…` links and nested `<a>` tags in breadcrumbs | `url_for('static', …)` and fixed breadcrumbs | templates | `test_static_assets_are_served` |
| Home and About pages contained template placeholder text, invented statistics and a fake contact form | Replaced with a description of how the system works | `index.html`, `about.html`, `footer.html` | Page tests |
| Template credit removed from the footer | Restored, as the BootstrapMade free license requires | `footer.html` | |
| Firmware: Wi-Fi password and server IP in the code | Moved to `config.h` (git-ignored) with `config.example.h` | firmware | Not compiled |
| Firmware: read functions called themselves after every tap | Removed the recursive call; `loop()` already polls again | firmware | Not compiled |
| Firmware: `sendData()` returned nothing when Wi-Fi was down | Returns an empty reply, so the red LED lights | firmware | Not compiled |
| Firmware: unused fourth reader, `sendData1()` posting to a route that does not exist, unused helpers | Removed (kept in the original copy) | firmware | Not compiled |
| Mixed Windows/Unix line endings | Unix line endings | all text files | |

Unchanged on purpose: the database schema and column names, the `/tryMy` request and its `100`/`101`
replies, the fare formula (₹4 per km, rounded), the timestamp format of the newer version, the reader
pins, and the page layouts.

## 6. Git history

The recovered code came with the git history of the original team repository, and earlier versions of
this repository contained uploaded project archives and documents. Neither belongs in the published
project, because they include files with personal data. In November 2026 the repository was therefore
restarted with a fresh history: its first commit contains only the cleaned project described in this log.
The earlier history is kept in private backups and not published.

## 7. Still to do

- Compile the firmware and test the readers, cards and LEDs on the physical model.
- Run one payment against Razorpay's test mode with real test keys.
- Decide on a licence once the ownership and permission questions are resolved (see the README).
