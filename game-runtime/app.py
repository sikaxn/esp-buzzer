from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import esp32_handler

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

# New event push API
def send_winner(mac):
    socketio.emit('winner', {'mac': mac})

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
