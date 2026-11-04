// Copy this file to config.h (same folder) and fill in your own values.
// config.h is ignored by git so your Wi-Fi password is never committed.

#define WIFI_SSID "your-wifi-name"
#define WIFI_PASSWORD "your-wifi-password"

// IPv4 address of the computer running the Flask server, on the same Wi-Fi network as the ESP32.
// Find it with `ipconfig` (Windows), `ipconfig getifaddr en0` (macOS) or `hostname -I` (Linux).
#define SERVER_URL "http://192.168.1.10:5000/tryMy"
