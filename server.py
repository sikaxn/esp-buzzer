import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import threading
import time
import json

UDP_PORT = 4210
KEEPALIVE_TIMEOUT = 15  # seconds

# Global device tracking
devices = {}
buzz_buffer = []
buzz_window_active = False
start_button_enabled = False
window_start_time = 0
winner_mac = None

# GUI Setup
root = tk.Tk()
root.title("ESP32 Buzzer Server")

# Treeview Frame
device_frame = ttk.LabelFrame(root, text="Connected Devices")
device_frame.pack(fill="x", padx=10, pady=5)

columns = ("ip", "id", "last_seen", "last_button")
device_tree = ttk.Treeview(device_frame, columns=columns, show="headings")
for col in columns:
    device_tree.heading(col, text=col.capitalize().replace("_", " "))
    device_tree.column(col, stretch=True)
device_tree.pack(fill="x", padx=5, pady=5)

def highlight_row(mac, color):
    for item in device_tree.get_children():
        if device_tree.item(item)['values'][1] == mac:
            device_tree.item(item, tags=("highlight",))
            device_tree.tag_configure("highlight", background=color)
            break

def clear_row_colors():
    for item in device_tree.get_children():
        device_tree.item(item, tags=())

# Log Frame
log_frame = ttk.LabelFrame(root, text="Log")
log_frame.pack(fill="both", expand=True, padx=10, pady=5)

log_box = scrolledtext.ScrolledText(log_frame, height=10, state='disabled')
log_box.pack(fill="both", expand=True)

def log(message):
    log_box.configure(state='normal')
    log_box.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
    log_box.configure(state='disabled')
    log_box.yview(tk.END)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', UDP_PORT))
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

def udp_listener():
    global buzz_window_active, buzz_buffer, window_start_time, winner_mac
    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except Exception as e:
            log(f"[ERROR] Socket error: {e}")
            continue

        ip = addr[0]
        now = time.time()

        try:
            msg = json.loads(data.decode())
            mtype = msg.get("type")

            if mtype == "buzz":
                mac = msg.get("mac")
                button = msg.get("button")
                timestamp = msg.get("timestamp")

                dev = devices.setdefault(mac, {"ip": ip, "mac": mac, "last_seen": now, "last_button": "-"})
                dev["ip"] = ip
                dev["last_seen"] = now
                dev["last_button"] = f"Button {button}"

                log(f"[BUZZ] MAC {mac} @ {ip} pressed Button {button} at {timestamp} ms")

                if buzz_window_active:
                    buzz_buffer.append({"mac": mac, "button": button, "timestamp": timestamp})

                elif start_button_enabled:
                    buzz_window_active = True
                    window_start_time = time.time()
                    buzz_buffer = [{"mac": mac, "button": button, "timestamp": timestamp}]
                    threading.Thread(target=buzz_window_timer, daemon=True).start()

        except json.JSONDecodeError:
            log(f"[ERROR] Invalid JSON from {ip}")

def buzz_window_timer():
    global buzz_window_active, buzz_buffer, start_button_enabled, winner_mac
    time.sleep(0.5)
    buzz_window_active = False
    start_button_enabled = False
    toggle_button.config(text="Start Buzz Round", bg="SystemButtonFace")

    if not buzz_buffer:
        log("[RESULT] No buzzes received in time window.")
        return

    earliest = min(buzz_buffer, key=lambda b: b["timestamp"])
    winner_mac = earliest["mac"]
    log(f"[RESULT] Winner: MAC {winner_mac} Button {earliest['button']} @ {earliest['timestamp']} ms")
    highlight_row(winner_mac, "lightgreen")
    buzz_buffer.clear()

def start_buzz_round():
    global start_button_enabled, winner_mac
    start_button_enabled = True
    winner_mac = None
    clear_row_colors()
    toggle_button.config(text="Stop Buzz Round", bg="red")
    log("[START] Ready to receive buzzes...")

def update_device_list():
    now = time.time()
    device_tree.delete(*device_tree.get_children())
    for mac, info in list(devices.items()):
        last_seen = int(now - info["last_seen"])
        row = device_tree.insert('', 'end', values=(
            info["ip"],
            mac,
            f"{last_seen}s ago",
            info["last_button"]
        ))
        if mac == winner_mac:
            device_tree.item(row, tags=("highlight",))
            device_tree.tag_configure("highlight", background="lightgreen")
    root.after(1000, update_device_list)

# Start Button
toggle_button = tk.Button(root, text="Start Buzz Round", command=start_buzz_round)
toggle_button.pack(pady=10)

# Threads
threading.Thread(target=udp_listener, daemon=True).start()
update_device_list()
root.mainloop()
