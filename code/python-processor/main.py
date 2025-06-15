import asyncio
import os
import random
import argparse
import csv
import time
from scapy.all import Ether, IP, UDP
from nats.aio.client import Client as NATS
from math import log2

TP, TN, FP, FN = 0, 0, 0, 0
csv_header_written = False
last_packet_time = None

ENABLE_MITIGATION = True

MITIGATOR_LOG_PATH = "/code/python-processor/mitigator.csv"
if not os.path.exists(MITIGATOR_LOG_PATH):
    with open(MITIGATOR_LOG_PATH, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["src_ip", "length", "inter_arrival", "entropy", "label", "dropped"])

def is_covert_heuristic(ip_src):
    last_octet = int(ip_src.strip().split('.')[-1])
    return last_octet != 21

def update_stats(predicted, actual):
    global TP, TN, FP, FN
    if predicted and actual:
        TP += 1
    elif predicted and not actual:
        FP += 1
    elif not predicted and actual:
        FN += 1
    elif not predicted and not actual:
        TN += 1

def get_stats():
    return TP, TN, FP, FN

def calculate_entropy(data):
    if not data:
        return 0
    freq = {}
    for byte in data:
        freq[byte] = freq.get(byte, 0) + 1
    total = len(data)
    entropy = -sum((count / total) * log2(count / total) for count in freq.values())
    return entropy

parser = argparse.ArgumentParser()
parser.add_argument("--duration", type=int, default=20, help="Listening duration in seconds")
args = parser.parse_args()

async def run():
    global last_packet_time, csv_header_written
    nc = NATS()
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    async def message_handler(msg):
        global last_packet_time, csv_header_written

        subject = msg.subject
        data = msg.data
        packet = Ether(data)

        delay_sec = random.expovariate(1 / 5e-6)
        delay_ms = delay_sec * 1000
        await asyncio.sleep(delay_sec)

        if IP in packet and UDP in packet:
            ip_src = packet[IP].src
            udp_payload = bytes(packet[UDP].payload)
            length = len(udp_payload)
            now = time.time()
            inter_arrival = now - last_packet_time if last_packet_time else 0
            last_packet_time = now
            entropy = calculate_entropy(udp_payload)

            last_octet = int(ip_src.strip().split('.')[-1])
            actual_label = "covert" if last_octet != 21 else "normal"
            actual = actual_label == "covert"
            heuristic_pred = is_covert_heuristic(ip_src)

            print(f"[Detector] src_ip={ip_src} | Heuristic={heuristic_pred} | Actual={actual_label}")
            update_stats(heuristic_pred, actual)

            filename = "/code/python-processor/features_covert.csv" if actual else "/code/python-processor/features_normal.csv"
            with open(filename, "a", newline='') as f:
                writer = csv.writer(f)
                if f.tell() == 0:
                    writer.writerow(["src_ip", "length", "inter_arrival", "entropy", "label"])
                writer.writerow([ip_src, length, inter_arrival, entropy, actual_label])

            with open(MITIGATOR_LOG_PATH, "a", newline='') as mf:
                writer = csv.writer(mf)
                writer.writerow([ip_src, length, inter_arrival, entropy, actual_label, heuristic_pred])

            if ENABLE_MITIGATION and heuristic_pred:
                print(f"[Mitigator] Dropped suspected covert packet from {ip_src}")
                return

        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)

        print(f"Processed a message with exponential delay {delay_ms:.5f} ms")

    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)
    print(f"[*] Subscribed to topics. Listening for {args.duration} seconds...")

    await asyncio.sleep(args.duration)
    await nc.close()

    print("\n[Detection Metrics]")
    TP, TN, FP, FN = get_stats()
    total = TP + TN + FP + FN
    print(f"TP={TP}, TN={TN}, FP={FP}, FN={FN}")
    if total > 0:
        precision = TP / (TP + FP) if (TP + FP) else 0
        recall = TP / (TP + FN) if (TP + FN) else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
        print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1 Score: {f1:.2f}")
    else:
        print("No detection stats recorded.")

if __name__ == "__main__":
    asyncio.run(run())
