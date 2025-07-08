# vesp32_handler.py

import time

devices = {}
mac_name_map = {}
on_devices_changed = None
on_winner = None

def handle_virtual_buzz(mac, button, client_ip="virtual"):
    now = time.time()

    label_ip = f"{client_ip} (virtual)"
    dev = devices.setdefault(mac, {
        "mac": mac,
        "ip": label_ip,
        "last_seen": now,
        "last_button": "-"
    })
    dev.update({
        "ip": label_ip,
        "last_seen": now,
        "last_button": f"Button {button}"
    })

    if on_devices_changed:
        on_devices_changed()

    import game_runner
    game_runner.handle_buzz(mac, button, int(now * 1000))



def get_devices():
    now = time.time()
    return [{
        "ip": info["ip"],
        "mac": mac,
        "name": mac_name_map.get(mac, ""),
        "last_seen": int(now - info["last_seen"]),
        "last_button": info["last_button"]
    } for mac, info in devices.items()]


def set_on_winner(cb):
    global on_winner
    on_winner = cb
    import game_runner
    game_runner.on_winner = cb


def set_on_devices_changed(cb):
    global on_devices_changed
    on_devices_changed = cb
