import socket
import time
import random

DEST_IP = "10.0.0.21"
DEST_PORT = 8888
NUM_PACKETS = 40

for i in range(NUM_PACKETS):
    msg_len = random.randint(20, 100)
    msg = bytes([random.randint(0, 255) for _ in range(msg_len)])
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg, (DEST_IP, DEST_PORT))
    sock.close()
    
    print(f"[Normal Sender] Sent packet {i+1} with {msg_len} bytes")
    time.sleep(0.1)
