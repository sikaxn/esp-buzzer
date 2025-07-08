# game_runner.py

import time
import threading

buzz_buffer = []
buzz_window_active = False
start_button_enabled = False
window_start_time = 0
winner_mac = None
on_winner = None

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

def handle_buzz(mac, button, timestamp):
    global buzz_window_active, buzz_buffer, window_start_time

    if buzz_window_active:
        buzz_buffer.append({"mac": mac, "button": button, "timestamp": timestamp})
    elif start_button_enabled:
        buzz_window_active = True
        window_start_time = time.time()
        buzz_buffer = [{"mac": mac, "button": button, "timestamp": timestamp}]
        threading.Thread(target=buzz_window_timer, daemon=True).start()

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
            on_winner({
                "mac": winner_mac,
                "button": button
            })
        except Exception as e:
            print(f"[ERROR] Failed to call on_winner: {e}")
    else:
        print("[DEBUG] on_winner is not set.")

    buzz_buffer.clear()
