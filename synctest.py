import socket
import struct
import json
import time

MULTICAST_GROUP = "239.1.2.3"
UDP_PORT = 4210

def millis():
    return int(time.time() * 1000)

def start_sync_simulator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', UDP_PORT))

    mreq = struct.pack("=4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"✅ Listening to multicast sync on {MULTICAST_GROUP}:{UDP_PORT}...")
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            msg = json.loads(data.decode())
            if msg.get("type") == "sync":
                server_time = msg["timestamp"]
                local_time = millis()
                offset = server_time - local_time
                print(f"[SYNC] Received: {server_time} ms | Local: {local_time} ms | Offset: {offset:+} ms")
        except Exception as e:
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    start_sync_simulator()
