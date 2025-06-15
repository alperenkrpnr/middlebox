import socket
import argparse
import os
import time

def start_udp_listener(port, donefile):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    print(f"[Receiver] Listening on port {port}...")

    decoded = ""
    while True:
        if os.path.exists(donefile):
            print("[Receiver] Done file detected. Exiting.")
            break
        try:
            sock.settimeout(1.0)
            data, addr = sock.recvfrom(4096)
            src_ip = addr[0]
            last_octet = int(src_ip.strip().split(".")[-1])
            char = chr(last_octet)
            decoded += char
            print(f"Received from {src_ip} -> '{char}'")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[Receiver] Error: {e}")
    print("[Receiver] Final decoded message:", decoded)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--donefile", default="/code/done.txt")
    args = parser.parse_args()
    start_udp_listener(args.port, args.donefile)
