import sys
sys.path.append('/code/sec/scapy-2.6.1')

import argparse
import time
from scapy.all import IP, UDP, send

parser = argparse.ArgumentParser()
parser.add_argument("--dst_ip", default="10.0.0.21", help="Destination IP (receiver)")
parser.add_argument("--dst_port", type=int, default=8888, help="Destination UDP port")
parser.add_argument("--delay", type=float, default=0.01, help="Delay between packets")
parser.add_argument("--message", default="Covert Channel Type is: Source and Destination Address Spoofing: Encoding data by altering source/destination addresses.", help="Message to send")

args = parser.parse_args()

for char in args.message:
    spoofed_ip = f"10.1.0.{ord(char)}"
    pkt = IP(src=spoofed_ip, dst=args.dst_ip) / UDP(sport=12345, dport=args.dst_port) / b"covert"
    send(pkt, verbose=False)
    print(f"Sent char '{char}' as spoofed IP {spoofed_ip}")
    time.sleep(args.delay)

print("[Sender] All characters sent.")
