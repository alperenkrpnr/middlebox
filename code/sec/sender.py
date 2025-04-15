import os
import time
import argparse
from scapy.all import IP, UDP, send

def encode_and_send(msg, dst_ip, dst_port, delay):
    for char in msg:
        spoofed_ip = f"10.1.0.{ord(char)}"
        pkt = IP(src=spoofed_ip, dst=dst_ip)/UDP(sport=12345, dport=dst_port)/b"covert"
        send(pkt, verbose=False)
        print(f"Sent char '{char}' as spoofed IP {spoofed_ip}")
        time.sleep(delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dst_ip", type=str, default=os.getenv("INSECURENET_HOST_IP", "10.0.0.21"))
    parser.add_argument("--dst_port", type=int, default=8888)
    parser.add_argument("--msg", type=str, default="Alperen's Covert Channel !?$#")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between packets in seconds")
    args = parser.parse_args()

    encode_and_send(args.msg, args.dst_ip, args.dst_port, args.delay)
