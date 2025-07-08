import socket
import threading
import time
import json
import game_runner  # ⬅️ import new module

UDP_PORT = 4210
KEEPALIVE_TIMEOUT = 15  # seconds

devices = {}
mac_name_map = {}

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

                if on_devices_changed:
                    on_devices_changed()

                # Delegate buzz handling to game_runner
                game_runner.handle_buzz(mac, button, timestamp)

        except Exception as e:
            print(f"[UDP ERROR] {e}")




def get_devices():
    now = time.time()
    return [{
        "ip": info["ip"],
        "mac": mac,
        "name": mac_name_map.get(mac, ""),
        "last_seen": int(now - info["last_seen"]),
        "last_button": info["last_button"]
    } for mac, info in devices.items()]


def get_winner():
    return game_runner.winner_mac


def set_on_winner(cb):
    global on_winner
    on_winner = cb
    game_runner.on_winner = cb


def set_on_devices_changed(cb):
    global on_devices_changed
    on_devices_changed = cb
