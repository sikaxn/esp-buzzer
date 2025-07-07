from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import esp32_handler
import json
import os

import json
import os

assignment_file = os.path.join(os.path.dirname(__file__), "assignment.json")
if os.path.exists(assignment_file):
    with open(assignment_file, "r") as f:
        mac_name_map = json.load(f)
else:
    mac_name_map = {}

# Inject into esp32_handler
esp32_handler.mac_name_map = mac_name_map


app = Flask(__name__, static_folder='static', template_folder='templates')
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('control.html')

@app.route('/projector')
def projector():
    return render_template('projector.html')

@app.route('/control')
def control():
    return render_template('control.html')

@app.route('/api/start', methods=['POST'])
def api_start():
    esp32_handler.start_buzz_round()
    return jsonify({"status": "started"})

@app.route('/api/stop', methods=['POST'])
def api_stop():
    esp32_handler.stop_buzz_round()
    return jsonify({"status": "stopped"})

@app.route("/broadcast")
def broadcast():
    return render_template("broadcast.html")

# New event push API
def send_winner(data):
    print("[SEND_WINNER] Send winner called")
    mac = data["mac"]
    button = data["button"]
    name = mac_name_map.get(mac, mac)
    print(f"[SEND_WINNER] Emitting: {name} (MAC: {mac}, Button: {button})")

    socketio.emit('winner', {
        "mac": mac,
        "button": button,
        "name": name
    })

def update_devices():
    socketio.emit('devices', esp32_handler.get_devices())

@socketio.on('projector_state')
def handle_projector_state(data):
    emit('projector_state', data, broadcast=True)


esp32_handler.on_winner = send_winner
esp32_handler.on_devices_changed = update_devices

if __name__ == '__main__':
    esp32_handler.start_udp_listener()
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)
