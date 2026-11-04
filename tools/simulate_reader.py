"""Simulate the ESP32 RFID reader by sending card taps to a running Smart Travel server.

Each tap is sent exactly as the firmware sends it: POST /tryMy with {"uid": " <uid>", "stp": "<stop>"}.
The server replies "100" (accepted, green LED) or "101" (rejected, red LED).

Example, a trip from stop1 to stop3 with the demo passenger card:
    python tools/simulate_reader.py --card "108 145 014 59" stop1 stop3
"""
import argparse
import json
import sys
import urllib.error
import urllib.request

REPLIES = {"100": "accepted (green LED)", "101": "rejected (red LED)"}


def send_tap(server, card, stop):
    # The firmware puts a space before every byte, so the UID it sends starts with a space.
    body = json.dumps({"uid": " " + card.strip(), "stp": stop}).encode()
    request = urllib.request.Request(server.rstrip("/") + "/tryMy", data=body,
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.read().decode().strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stops", nargs="+", help="stop codes to tap at, in order (e.g. stop1 stop3)")
    parser.add_argument("--card", required=True, help='card UID as stored in the database, e.g. "77 208 30 43"')
    parser.add_argument("--server", default="http://127.0.0.1:5000", help="server address (default: %(default)s)")
    args = parser.parse_args()

    for stop in args.stops:
        try:
            reply = send_tap(args.server, args.card, stop)
        except urllib.error.URLError as error:
            sys.exit(f"Could not reach {args.server}: {error.reason}")
        print(f"{stop}: {reply} {REPLIES.get(reply, '(unexpected reply)')}")


if __name__ == "__main__":
    main()
