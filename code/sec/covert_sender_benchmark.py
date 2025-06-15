"""
#this code was perfectly working, I added an error rate to simulate errors in the covert channel
import time
from scapy.all import IP, UDP, send
import random

message = "This is covert!"
delay = 0.1  # seconds

def char_to_ip(c):
    return f"10.1.0.{ord(c)}"

for ch in message:
    ip = char_to_ip(ch)
    packet = IP(src=ip, dst="10.0.0.21")/UDP(sport=random.randint(1000, 50000), dport=1234)/b"x"*20
    send(packet, verbose=False)
    print(f"Sent: {ch} as IP {ip}")
    time.sleep(delay)
"""
import time
import random
from scapy.all import IP, UDP, send

MESSAGE = "this is a test message for confidence intervals"
DST_IP = "10.0.0.21"
DST_PORT = 8888
DELAY = 0.01
ERROR_RATE = 0.1

print("[Covert Sender] Starting benchmark transmission...")

for char in MESSAGE:
    ascii_val = ord(char)

    if random.random() < ERROR_RATE:
        fake_val = random.randint(1, 254)
        print(f"[ERROR] Sent wrong char '{char}' as spoofed IP 10.1.0.{fake_val}")
        ip_src = f"10.1.0.{fake_val}"
    else:
        print(f"[OK] Sent char '{char}' as spoofed IP 10.1.0.{ascii_val}")
        ip_src = f"10.1.0.{ascii_val}"

    pkt = IP(src=ip_src, dst=DST_IP) / UDP(sport=12345, dport=DST_PORT) / b"covert"
    send(pkt, verbose=False)
    time.sleep(DELAY)

print("[Covert Sender] Transmission complete.")
