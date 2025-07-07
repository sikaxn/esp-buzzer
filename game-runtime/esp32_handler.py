import socket
import threading
import time
import json

UDP_PORT = 4210
KEEPALIVE_TIMEOUT = 15  # seconds

devices = {}
buzz_buffer = []
buzz_window_active = False
start_button_enabled = False
window_start_time = 0
winner_mac = None
mac_name_map = {}  # ✅ add this at the top


on_winner = None
on_devices_changed = None


sock = None  # <-- Declare globally


def start_udp_listener():
    global sock
    if sock is None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', UDP_PORT))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        threading.Thread(target=udp_listener, daemon=True).start()
        print(f"[UDP] Listening on port {UDP_PORT}")


def udp_listener():
    global buzz_window_active, buzz_buffer, window_start_time, winner_mac
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            ip = addr[0]
            now = time.time()

            msg = json.loads(data.decode())
            mtype = msg.get("type")

            if mtype == "buzz":
                mac = msg.get("mac")
                button = msg.get("button")
                timestamp = msg.get("timestamp")

                # Update or create device entry
                dev = devices.setdefault(mac, {
                    "ip": ip,
                    "mac": mac,
                    "last_seen": now,
                    "last_button": "-"
                })
                dev.update({
                    "ip": ip,
                    "last_seen": now,
                    "last_button": f"Button {button}"
                })

                # Notify frontend of updated devices
                if on_devices_changed:
                    on_devices_changed()

                # Handle buzz round window
                if buzz_window_active:
                    buzz_buffer.append({"mac": mac, "button": button, "timestamp": timestamp})
                elif start_button_enabled:
                    buzz_window_active = True
                    window_start_time = time.time()
                    buzz_buffer = [{"mac": mac, "button": button, "timestamp": timestamp}]
                    threading.Thread(target=buzz_window_timer, daemon=True).start()

        except Exception as e:
            print(f"[UDP ERROR] {e}")



def buzz_window_timer():
    global buzz_window_active, buzz_buffer, start_button_enabled, winner_mac
    time.sleep(0.5)
    buzz_window_active = False
    start_button_enabled = False

    if not buzz_buffer:
        print("[RESULT] No buzzes received in time window.")
        return

    earliest = min(buzz_buffer, key=lambda b: b["timestamp"])
    winner_mac = earliest["mac"]
    button = earliest["button"]
    timestamp = earliest["timestamp"]

    print(f"[RESULT] Winner: MAC {winner_mac} Button {button} @ {timestamp} ms")

    if on_winner:
        try:
            print("[DEBUG] Calling on_winner callback...")
            on_winner({
                "mac": winner_mac,
                "button": button
            })
        except Exception as e:
            print(f"[ERROR] Failed to call on_winner: {e}")
    else:
        print("[DEBUG] on_winner is not set.")

    buzz_buffer.clear()


def start_buzz_round():
    global start_button_enabled, winner_mac
    start_button_enabled = True
    winner_mac = None
    print("[START] Ready to receive buzzes...")


def stop_buzz_round():
    global start_button_enabled, buzz_window_active
    start_button_enabled = False
    buzz_window_active = False
    print("[STOP] Buzz round manually stopped.")


def get_devices():
    now = time.time()
    return [{
        "ip": info["ip"],
        "mac": mac,
        "name": mac_name_map.get(mac, ""),  # ✅ use injected map
        "last_seen": int(now - info["last_seen"]),
        "last_button": info["last_button"]
    } for mac, info in devices.items()]


def get_winner():
    return winner_mac
