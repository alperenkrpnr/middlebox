import subprocess
import time
import numpy as np
from scipy import stats
import os
import signal
import csv

SENDER_PATH = os.path.join("..", "sec", "sender.py")
RECEIVER_PATH = os.path.join("..", "insec", "receiver.py")
CSV_PATH = "benchmark_results.csv"

def start_receiver():
    print("[*] Starting receiver...")
    proc = subprocess.Popen(
        ["python3", RECEIVER_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    time.sleep(1)
    return proc

def stop_receiver(proc):
    print("[*] Stopping receiver...")
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)

def run_benchmark(message, delay, trials):
    durations = []

    receiver_proc = start_receiver()

    try:
        print(f"\n[!] Benchmarking '{message}' | delay={delay}s | trials={trials}\n")

        for i in range(trials):
            try:
                start = time.time()

                result = subprocess.run([
                    "python3", SENDER_PATH,
                    "--msg", message,
                    "--delay", str(delay)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

                end = time.time()

                if result.returncode != 0:
                    print(f"Trial {i+1}: Sender failed. Error:\n{result.stderr.decode().strip()}")
                    continue

                duration = end - start
                if duration <= 0:
                    print(f"Trial {i+1}: Invalid timing (duration={duration:.3f}), skipping.")
                    continue

                durations.append(duration)
                print(f"Trial {i+1}: {duration:.3f} sec")

            except Exception as e:
                print(f"Trial {i+1}: Exception occurred: {e}")

        durations = np.array(durations)
        mean = durations.mean()
        std_err = stats.sem(durations)
        ci_low, ci_high = stats.t.interval(0.95, len(durations) - 1, loc=mean, scale=std_err)

        bits_sent = len(message) * 8
        capacity_bps = bits_sent / mean

        print("\n==== Benchmark Results ====")
        print(f"Message sent: '{message}' ({len(message)} characters → {len(message)*8} bits)")
        print(f"Average total time to send message: {mean:.3f} seconds")
        print(f"95% Confidence Interval of duration: ({ci_low:.3f}, {ci_high:.3f}) seconds")
        print(f"Estimated channel capacity: {capacity_bps:.2f} bits per second")

        write_csv(message, delay, trials, mean, ci_low, ci_high, capacity_bps)

    finally:
        stop_receiver(receiver_proc)

def write_csv(message, delay, trials, mean, ci_low, ci_high, capacity):
    header = ["Message", "Delay(s)", "Trials", "Mean Time(s)", "CI Lower", "CI Upper", "Capacity (bits/sec)"]
    file_exists = os.path.exists(CSV_PATH)

    with open(CSV_PATH, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerow([message, delay, trials, f"{mean:.3f}", f"{ci_low:.3f}", f"{ci_high:.3f}", f"{capacity:.2f}"])

if __name__ == "__main__":
    # Default
    default_message = "Alperen's Covert Channel!!!"
    default_delay = 0.1
    default_trials = 10

    msg_input = input(f"Enter message (default = '{default_message}'): ").strip()
    delay_input = input(f"Enter inter-packet delay in seconds (default = {default_delay}): ").strip()
    trials_input = input(f"Enter number of trials (default = {default_trials}): ").strip()

    message = msg_input if msg_input else default_message
    delay = float(delay_input) if delay_input else default_delay
    trials = int(trials_input) if trials_input else default_trials

    run_benchmark(
        message=message,
        delay=delay,
        trials=trials
    )
