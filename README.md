# Smart Travel - RFID-Based Automated Bus Ticketing System

## Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Hardware Components](#hardware-components)
4. [Software Components](#software-components)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [User Workflow](#user-workflow)
8. [Installation Guide](#installation-guide)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)
12. [Future Enhancements](#future-enhancements)

---

## Project Overview

### Introduction

Smart Travel is an IoT-based automated bus ticketing system that revolutionizes public transportation payments using RFID (Radio Frequency Identification) technology. The system eliminates the need for physical tickets or cash transactions, providing a seamless, contactless payment experience for commuters.

### Problem Statement

Traditional bus ticketing systems face several challenges:
- Long queues for ticket purchase
- Handling of physical cash and change
- Ticket fraud and revenue leakage
- Difficulty in tracking passenger travel patterns
- Inefficient fare calculation for distance-based pricing

### Solution

Smart Travel addresses these challenges by implementing:
- Contactless RFID card-based entry and exit at bus stops
- Automatic fare calculation based on distance traveled
- Online payment integration through Razorpay
- Complete travel history tracking
- Admin dashboard for user management

### Key Features

| Feature | Description |
|---------|-------------|
| **RFID Card Integration** | Each user is assigned a unique RFID card for identification |
| **Distance-Based Fare** | Automatic fare calculation at ₹4 per kilometer |
| **Online Payment** | Secure payment processing via Razorpay gateway |
| **Travel History** | Complete record of all journeys with timestamps |
| **Admin Panel** | User management, RFID assignment, and user removal |
| **Real-time Processing** | Instant card detection and server communication |
| **LED Feedback** | Visual indicators for successful/failed transactions |

---

## System Architecture

### High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SMART TRAVEL SYSTEM                              │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │   Station 1   │    │   Station 2   │    │   Station 3   │           │
│  │ RFID + ESP32  │    │ RFID + ESP32  │    │ RFID + ESP32  │           │
│  │ + LED (G/R)   │    │ + LED (G/R)   │    │ + LED (G/R)   │           │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘           │
│          │                    │                    │                    │
│          └────────────────────┼────────────────────┘                    │
│                               │                                         │
│                        ┌──────┴──────┐                                  │
│                        │ WiFi Network│                                  │
│                        └──────┬──────┘                                  │
│                               │                                         │
│  ┌────────────────────────────┴────────────────────────────────┐       │
│  │                    FLASK WEB SERVER                          │       │
│  │  Routes Handler | SQLite Database | Razorpay Integration     │       │
│  └────────────────────────────┬────────────────────────────────┘       │
│                               │                                         │
│  ┌────────────────────────────┴────────────────────────────────┐       │
│  │     WEB INTERFACE: Home | Login | Profile | Admin Panel      │       │
│  └──────────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Card Tap at Entry Station**
   - User taps RFID card at bus stop reader
   - ESP32 reads card UID and station identifier
   - Data sent to Flask server via HTTP POST
   - Server creates new task entry with timestamp

2. **Card Tap at Exit Station**
   - User taps same RFID card at destination
   - ESP32 sends card UID and station identifier
   - Server calculates distance and fare
   - Task entry updated with exit details

3. **Payment Processing**
   - User logs into web portal
   - Views pending dues on profile page
   - Initiates payment via Razorpay
   - Transaction recorded in history

---

## Hardware Components

### Bill of Materials

| Component | Quantity | Specification | Purpose |
|-----------|----------|---------------|---------|
| ESP32 Development Board | 1 | ESP32-WROOM-32 | Main microcontroller with WiFi |
| MFRC522 RFID Reader | 3 | 13.56 MHz | Card reading at each station |
| RFID Cards/Tags | Multiple | MIFARE Classic 1K | User identification |
| LEDs (Green) | 3 | 5mm | Success indicator |
| LEDs (Red) | 3 | 5mm | Failure indicator |
| Resistors | 6 | 220Ω | LED current limiting |
| Jumper Wires | Multiple | Male-to-Male | Connections |
| Breadboard | 1 | Standard | Prototyping |
| USB Cable | 1 | Micro USB | Programming & Power |

### Pin Configuration

#### ESP32 to RFID Reader Connections

| RFID Reader | ESP32 Pin | Description |
|-------------|-----------|-------------|
| SDA (SS) - Reader 1 | GPIO 21 | Slave Select for Reader 1 |
| SDA (SS) - Reader 2 | GPIO 22 | Slave Select for Reader 2 |
| SDA (SS) - Reader 3 | GPIO 2 | Slave Select for Reader 3 |
| SCK | GPIO 18 | SPI Clock |
| MOSI | GPIO 23 | Master Out Slave In |
| MISO | GPIO 19 | Master In Slave Out |
| RST | GPIO 4 | Reset (Shared) |
| VCC | 3.3V | Power Supply |
| GND | GND | Ground |

#### LED Connections

| LED | ESP32 Pin | Description |
|-----|-----------|-------------|
| Station 1 - Green | GPIO 12 | Success indicator |
| Station 1 - Red | GPIO 14 | Failure indicator |
| Station 2 - Green | GPIO 27 | Success indicator |
| Station 2 - Red | GPIO 26 | Failure indicator |
| Station 3 - Green | GPIO 25 | Success indicator |
| Station 3 - Red | GPIO 33 | Failure indicator |

### Circuit Diagram Description

```
                    ESP32 Development Board
                    ┌─────────────────────┐
                    │                     │
    RFID Reader 1 ──┤ GPIO 21 (SS1)       │
    RFID Reader 2 ──┤ GPIO 22 (SS2)       │
    RFID Reader 3 ──┤ GPIO 2  (SS3)       │
                    │                     │
    All Readers ────┤ GPIO 4  (RST)       │
                    │ GPIO 18 (SCK)       │
                    │ GPIO 23 (MOSI)      │
                    │ GPIO 19 (MISO)      │
                    │                     │
    LED Green 1 ────┤ GPIO 12             │
    LED Red 1 ──────┤ GPIO 14             │
    LED Green 2 ────┤ GPIO 27             │
    LED Red 2 ──────┤ GPIO 26             │
    LED Green 3 ────┤ GPIO 25             │
    LED Red 3 ──────┤ GPIO 33             │
                    │                     │
                    │ 3.3V ───────────────┼──── RFID VCC
                    │ GND ────────────────┼──── Common Ground
                    └─────────────────────┘
```

### Hardware Assembly Steps

1. **ESP32 Setup**
   - Place ESP32 on breadboard
   - Connect USB cable for power and programming

2. **RFID Reader Installation**
   - Connect all three RFID readers to shared SPI bus (SCK, MOSI, MISO)
   - Each reader gets unique SS (Slave Select) pin
   - Share RST pin across all readers
   - Connect VCC to 3.3V and GND to ground

3. **LED Installation**
   - Connect LEDs through 220Ω resistors
   - Green LEDs indicate successful transactions
   - Red LEDs indicate failed transactions or errors

4. **Final Verification**
   - Verify all connections before powering on
   - Check for short circuits
   - Ensure proper voltage levels (3.3V for RFID readers)

---

## Software Components

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | HTML5/CSS3 | - | User interface |
| **Frontend Framework** | Bootstrap | 5.1.3 | Responsive design |
| **Backend** | Python Flask | 2.0.2 | Web server & API |
| **Database** | SQLite | - | Data persistence |
| **ORM** | SQLAlchemy | 1.4.36 | Database operations |
| **Payment** | Razorpay | 1.3.0 | Payment processing |
| **Hardware** | Arduino/C++ | - | ESP32 programming |
| **Authentication** | Flask-Login | - | User sessions |
| **Forms** | Flask-WTF | 1.0.0 | Form validation |

### Project Structure

```
Smart_Travel_code_files/
│
├── SmartTravel_main_code/
│   │
│   ├── main.py                     # Main Flask application
│   ├── forms.py                    # WTForms definitions
│   ├── requirements.txt            # Python dependencies
│   ├── Procfile                    # Deployment configuration
│   ├── Travel.db                   # SQLite database file
│   │
│   ├── templates/                  # HTML templates
│   │   ├── index.html              # Home page
│   │   ├── header.html             # Common header component
│   │   ├── footer.html             # Common footer component
│   │   ├── LOGIN.html              # Login page
│   │   ├── REGISTER.html           # Registration page
│   │   ├── PROFILE.html            # User profile & payment
│   │   ├── admin.html              # Admin dashboard
│   │   ├── admin_profile.html      # Admin user details
│   │   ├── about_us.html           # About page
│   │   └── successful_payment.html # Payment confirmation
│   │
│   ├── static/                     # Static assets
│   │   ├── assets/
│   │   │   ├── css/                # Stylesheets
│   │   │   ├── js/                 # JavaScript files
│   │   │   ├── img/                # Images
│   │   │   ├── vendor/             # Third-party libraries
│   │   │   └── my_pay_script/      # Razorpay integration
│   │   ├── form_assets/            # Form styling
│   │   └── log_reg_assets/         # Login/Register styling
│   │
│   ├── forms/
│   │   └── contact.php             # Contact form handler
│   │
│   └── favicon_io/                 # Favicon files
│
└── trying_code/
    └── trying_code.ino             # Arduino/ESP32 firmware

```

### Flask Application (main.py)

The main Flask application handles all server-side logic:

#### Key Imports and Initialization

```python
from flask import Flask, render_template, redirect, url_for, flash, abort, request
from flask_bootstrap import Bootstrap
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import razorpay
```

#### Application Configuration

- **Secret Key**: Loaded from environment variable for session security
- **Database**: SQLite database (Travel.db) for data persistence
- **Bootstrap**: Integrated for responsive UI components
- **Login Manager**: Handles user authentication sessions

### Arduino Firmware (trying_code.ino)

The ESP32 firmware handles RFID reading and server communication:

#### Key Libraries

```cpp
#include <SPI.h>          // SPI communication
#include <MFRC522.h>      // RFID reader library
#include <HTTPClient.h>   // HTTP requests
#include <WiFi.h>         // WiFi connectivity
#include <ArduinoJson.h>  // JSON serialization
```

#### Core Functions

| Function | Purpose |
|----------|---------|
| `setup()` | Initialize WiFi, SPI, RFID readers, and LED pins |
| `loop()` | Continuously check all RFID readers for card presence |
| `readRFID1()` | Read card from Station 1 reader |
| `readRFID2()` | Read card from Station 2 reader |
| `readRFID3()` | Read card from Station 3 reader |
| `printDec()` | Convert card UID to decimal string |
| `sendData()` | Send card data to Flask server via HTTP POST |

#### Communication Protocol

The Arduino sends JSON data to the server:

```json
{
    "uid": "77 208 30 43",
    "stp": "stop1"
}
```

Server Response Codes:
- `100` - Success (Transaction recorded)
- `101` - Failure (Card not registered, duplicate tap, or pending dues)

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐       ┌─────────────────────┐
│       USERS         │       │       TASKS         │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │───────│ id (PK)             │
│ rfid (UNIQUE)       │       │ passenger_id (FK)   │
│ name                │       │ uid_1               │
│ email (UNIQUE)      │       │ dec_1               │
│ password (HASHED)   │       │ uid_2               │
└─────────────────────┘       │ dec_2               │
                              │ distance            │
                              │ due                 │
                              │ initial_timestamp   │
                              │ final_timestamp     │
                              └─────────────────────┘

┌─────────────────────┐       ┌─────────────────────┐
│      STATIONS       │       │    USER_HISTORY     │
├─────────────────────┤       ├─────────────────────┤
│ id (PK)             │       │ id (PK)             │
│ station_name        │       │ card                │
│ station_hexa        │       │ _from               │
│ distance_from_      │       │ _to                 │
│   initial           │       │ _from_time          │
└─────────────────────┘       │ _to_time            │
                              │ travel_distance     │
                              │ order_payment_id    │
                              │ ticket_due          │
                              └─────────────────────┘
```

### Table Descriptions

#### Users Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique user identifier |
| rfid | String(250) | UNIQUE, NULLABLE | RFID card number |
| name | String(250) | NOT NULL | User's full name |
| email | String(250) | UNIQUE, NOT NULL | User's email address |
| password | String(250) | NOT NULL | Hashed password |

#### Tasks Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique task identifier |
| passenger_id | Integer | FOREIGN KEY | Reference to users table |
| uid_1 | String(250) | UNIQUE | Entry RFID card number |
| dec_1 | String(250) | - | Entry station identifier |
| uid_2 | String(250) | - | Exit RFID card number |
| dec_2 | String(250) | - | Exit station identifier |
| distance | Float | - | Distance traveled in KM |
| due | String(250) | - | Fare amount in INR |
| initial_timestamp | String(250) | - | Entry time |
| final_timestamp | String(250) | - | Exit time |

#### Stations Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique station identifier |
| station_name | String(250) | UNIQUE, NOT NULL | Station display name |
| station_hexa | String(250) | UNIQUE, NOT NULL | Station code (stop1, stop2, etc.) |
| distance_from_initial | Float | NOT NULL | Distance from first station in KM |

#### UserHistory Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | PRIMARY KEY | Unique history identifier |
| card | String(250) | - | RFID card number |
| _from | String(250) | - | Origin station name |
| _to | String(250) | - | Destination station name |
| _from_time | String(250) | - | Journey start time |
| _to_time | String(250) | - | Journey end time |
| travel_distance | Float | - | Distance traveled |
| order_payment_id | String(250) | - | Razorpay order ID |
| ticket_due | Integer | - | Fare amount paid |

---

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET/POST | `/register` | User registration |
| GET/POST | `/login` | User login |
| GET | `/about` | About us page |

### Protected Endpoints (Login Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/profile` | User profile and payment |
| GET/POST | `/logout` | User logout |
| GET/POST | `/process_pay` | Process payment via Razorpay |

### Admin Endpoints (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/admin` | Admin dashboard - view all users |
| GET | `/user_details` | View specific user details |
| GET/POST | `/admin/delete_user` | Delete a user |
| GET/POST | `/admin/add_rfid` | Assign RFID to user |

### IoT Endpoint (Hardware Communication)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tryMy` | Receive RFID tap data from ESP32 |

#### /tryMy Endpoint Details

**Request Body:**
```json
{
    "uid": "77 208 30 43",
    "stp": "stop1"
}
```

**Response Codes:**
- `100` - Success
- `101` - Failure

**Logic Flow:**
1. Check if RFID is registered
2. If no existing task, create new entry (boarding)
3. If existing task without due, complete journey (alighting)
4. Calculate distance and fare
5. Return appropriate response code

---

## User Workflow

### New User Registration Flow

```
┌─────────────────┐
│   User visits   │
│   website       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Click "Get     │
│  Started"       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Fill register  │
│  form           │
│  - Name         │
│  - Email        │
│  - Password     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Account        │
│  created        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Admin assigns  │
│  RFID card      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User can now   │
│  travel         │
└─────────────────┘
```

### Travel and Payment Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     JOURNEY START                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  1. User taps RFID card at ENTRY station                    │
│     - ESP32 reads card UID                                  │
│     - Sends data: {"uid": "xxx", "stp": "stop1"}           │
│     - Server creates Task entry with timestamp              │
│     - Green LED blinks (Success)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  2. User travels on bus                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  3. User taps RFID card at EXIT station                     │
│     - ESP32 reads card UID                                  │
│     - Sends data: {"uid": "xxx", "stp": "stop2"}           │
│     - Server calculates distance and fare                   │
│     - Fare = Distance × ₹4/km                              │
│     - Task updated with exit details                        │
│     - Green LED blinks (Success)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     PAYMENT PROCESS                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. User logs into web portal                               │
│     - Views profile page                                    │
│     - Sees pending dues                                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. User clicks "Pay" button                                │
│     - Razorpay checkout opens                               │
│     - User completes payment                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  6. Payment confirmed                                       │
│     - Receipt displayed                                     │
│     - Entry moved to UserHistory                            │
│     - Task deleted                                          │
│     - User can travel again                                 │
└─────────────────────────────────────────────────────────────┘
```

### Admin Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Login as       │────▶│  View all       │────▶│  Select user    │
│  Admin (id=1)   │     │  users          │     │  for details    │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
         ┌───────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     USER MANAGEMENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐                 ┌─────────────────┐    │
│  │  Assign RFID    │                 │  Remove User    │    │
│  │  to new user    │                 │  from system    │    │
│  │                 │                 │                 │    │
│  │  - Enter RFID   │                 │  - Confirm      │    │
│  │    number       │                 │    deletion     │    │
│  │  - Submit       │                 │                 │    │
│  └─────────────────┘                 └─────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation Guide

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Arduino IDE 1.8 or higher
- ESP32 board support in Arduino IDE
- Git (optional, for version control)

### Software Setup

#### Step 1: Clone or Download the Project

```bash
# If using git
git clone <repository-url>
cd Smart_Travel_code_files/SmartTravel_main_code

# Or extract from provided ZIP/RAR file
```

#### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Python Dependencies

```bash
pip install flask
pip install flask-bootstrap
pip install flask-sqlalchemy
pip install flask-login
pip install flask-wtf
pip install razorpay
pip install python-dotenv
pip install werkzeug
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```env
APP_SECRET=your_secret_key_here
RAZOR_KEY=your_razorpay_key_id
RAZOR_SECRET=your_razorpay_secret_key
```

#### Step 5: Initialize Database

The database is automatically created when you first run the application. Pre-populate the Stations table:

```sql
INSERT INTO stations (station_name, station_hexa, distance_from_initial) VALUES
('Station A', 'stop1', 0.0),
('Station B', 'stop2', 5.0),
('Station C', 'stop3', 12.0);
```

#### Step 6: Get Your IPv4 Address

```bash
# On Windows:
ipconfig

# On macOS/Linux:
ifconfig
# or
ip addr
```

Note down the IPv4 address (e.g., `192.168.168.203`)

#### Step 7: Update main.py with IPv4

Edit `main.py` and update the last line:

```python
if __name__ == "__main__":
    app.run(debug=True, host='YOUR_IPV4_ADDRESS')
```

#### Step 8: Run Flask Application

```bash
python main.py
```

The server will start at `http://YOUR_IPV4_ADDRESS:5000`

### Hardware Setup

#### Step 1: Install Arduino IDE

1. Download Arduino IDE from https://www.arduino.cc/en/software
2. Install ESP32 board support:
   - Go to File → Preferences
   - Add to Additional Board Manager URLs:
     `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Go to Tools → Board → Boards Manager
   - Search "ESP32" and install

#### Step 2: Install Required Libraries

In Arduino IDE, go to Sketch → Include Library → Manage Libraries:
- **MFRC522** by GithubCommunity
- **ArduinoJson** by Benoit Blanchon

#### Step 3: Configure Arduino Code

Edit `trying_code.ino`:

```cpp
// Update WiFi credentials
char* ssid = "YOUR_WIFI_SSID";
char* pass = "YOUR_WIFI_PASSWORD";

// Update server URL with your IPv4
http.begin(client, "http://YOUR_IPV4_ADDRESS:5000/tryMy");
```

#### Step 4: Upload to ESP32

1. Connect ESP32 via USB
2. Select correct board: Tools → Board → ESP32 Dev Module
3. Select correct port: Tools → Port → (Your COM port)
4. Click Upload button
5. Open Serial Monitor (115200 baud) to verify

---

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `APP_SECRET` | Flask session secret key | `mysupersecretkey123` |
| `RAZOR_KEY` | Razorpay API Key ID | `rzp_test_xxxxx` |
| `RAZOR_SECRET` | Razorpay API Secret | `xxxxxxxxxxxxx` |

### Razorpay Setup

1. Create account at https://razorpay.com
2. Go to Settings → API Keys
3. Generate Test/Live API keys
4. Add to `.env` file

### Fare Configuration

Current fare calculation in `main.py`:

```python
ticket_cost = abs(round(distance_travelled * 4, 0))  # ₹4 per km
```

To modify fare rate, change the multiplier (currently `4`).

### Adding New Stations

Insert new stations into the database:

```sql
INSERT INTO stations (station_name, station_hexa, distance_from_initial)
VALUES ('New Station', 'stop4', 18.5);
```

Update Arduino code to handle new station identifier.

---

## Troubleshooting

### Common Issues and Solutions

#### 1. WiFi Connection Failed (Arduino)

**Symptoms:** Serial monitor shows "Waiting for connection" indefinitely

**Solutions:**
- Verify WiFi credentials in Arduino code
- Ensure ESP32 is within WiFi range
- Check if router allows new device connections
- Restart ESP32

#### 2. RFID Card Not Detected

**Symptoms:** No response when card is tapped

**Solutions:**
- Check RFID reader connections
- Verify 3.3V power supply to readers
- Ensure card is compatible (MIFARE Classic)
- Check SPI connections (SCK, MOSI, MISO)
- Test each reader individually

#### 3. Server Connection Error (Arduino)

**Symptoms:** HTTP code -1 or connection refused

**Solutions:**
- Verify server is running
- Check IPv4 address in Arduino code
- Ensure both devices on same network
- Check firewall settings
- Verify port 5000 is not blocked

#### 4. Red LED Always Blinking

**Symptoms:** All transactions show failure

**Solutions:**
- Check if RFID card is registered in database
- Verify user has assigned RFID
- Check for pending unpaid dues
- Review server logs for errors

#### 5. Database Errors

**Symptoms:** SQLAlchemy errors in console

**Solutions:**
- Delete `Travel.db` and restart (loses data)
- Check database file permissions
- Verify SQLAlchemy version compatibility

#### 6. Payment Not Processing

**Symptoms:** Razorpay checkout doesn't open

**Solutions:**
- Verify Razorpay API keys in `.env`
- Check browser console for errors
- Ensure HTTPS in production
- Verify Razorpay account is active

#### 7. Admin Access Denied

**Symptoms:** 403 Forbidden error on admin routes

**Solutions:**
- Admin is always user with `id=1`
- First registered user becomes admin
- Check if logged in as correct user

### Debug Tips

- Enable Flask debug mode: `app.run(debug=True, host='YOUR_IPV4')`
- Monitor Arduino via Serial Monitor at 115200 baud
- **Warning:** Disable debug mode in production!

---

## Security Considerations

### Current Security Features

| Feature | Implementation |
|---------|---------------|
| Password Hashing | PBKDF2 with SHA256 |
| Session Management | Flask-Login with secure cookies |
| CSRF Protection | Flask-WTF built-in |
| Admin Restriction | Decorator-based access control |
| SQL Injection Prevention | SQLAlchemy ORM |

### Recommended Security Enhancements

#### 1. Use HTTPS in Production

```python
# Use a production WSGI server
gunicorn --certfile=cert.pem --keyfile=key.pem -b 0.0.0.0:443 main:app
```

#### 2. Implement Rate Limiting

```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)

@app.route('/tryMy', methods=['POST'])
@limiter.limit("10 per minute")
def get_json():
    # ... existing code
```

#### 3. Add API Authentication for IoT

```python
# Add API key verification for Arduino requests
API_KEY = os.environ.get("IOT_API_KEY")

@app.route('/tryMy', methods=['POST'])
def get_json():
    if request.headers.get('X-API-Key') != API_KEY:
        return abort(401)
    # ... existing code
```

#### 4. Environment Variable Security

- Never commit `.env` file to version control
- Use different keys for development and production
- Rotate API keys periodically

#### 5. Input Validation

```python
# Validate RFID format
import re
def validate_rfid(rfid):
    pattern = r'^[\d\s]+$'
    return bool(re.match(pattern, rfid))
```

---

## Future Enhancements

### Planned Features

| Feature | Priority | Description |
|---------|----------|-------------|
| **Mobile App** | High | Android/iOS app for profile and payments |
| **QR Code Support** | High | Alternative to RFID cards |
| **Balance Prepaid** | High | Wallet system with prepaid balance |
| **SMS Notifications** | Medium | Journey and payment alerts |
| **Route Optimization** | Medium | Suggest optimal routes |
| **Analytics Dashboard** | Medium | Travel statistics and insights |
| **Multi-language** | Low | Support for regional languages |
| **Loyalty Program** | Low | Points and rewards system |

### Technical Improvements

- Move from SQLite to PostgreSQL for production
- Implement Redis for session caching
- Deploy with Gunicorn/uWSGI and nginx
- Add unit and integration tests

---

## Support and Contact

For technical support or queries, contact the project team.

---

## License

This project is proprietary and confidential.

© 2024 Smart Travel. All Rights Reserved.

---

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed via pip
- [ ] `.env` file configured with Razorpay keys
- [ ] IPv4 address updated in main.py and Arduino code
- [ ] Flask server running on port 5000
- [ ] Arduino IDE with ESP32 support installed
- [ ] Hardware assembled and code uploaded
- [ ] First user registered (becomes admin)
- [ ] RFID cards assigned via admin panel
- [ ] Test journey completed successfully

---

*Document Version: 1.0 | Last Updated: November 2024*


