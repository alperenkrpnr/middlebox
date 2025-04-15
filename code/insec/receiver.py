import socket
import argparse

def start_udp_listener(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", port))
    print(f"Receiver listening on UDP port {port}...")

    decoded_message = ""

    while True:
        data, address = sock.recvfrom(4096)
        src_ip = address[0]
        try:
            last_octet = int(src_ip.strip().split(".")[-1])
            char = chr(last_octet)
            decoded_message += char
            print(f"Received from spoofed IP {src_ip} -> Decoded: '{char}' | Message so far: '{decoded_message}'")
        except Exception as e:
            print(f"Error decoding from {src_ip}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
    start_udp_listener(args.port)
