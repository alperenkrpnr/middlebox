import subprocess
import os

def get_container_id_by_name(container_name):
    docker_ps_cmd = "docker ps --format '{{.ID}}\t{{.Names}}'"
    result = subprocess.run(docker_ps_cmd, shell=True, check=True, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in result.stdout.splitlines():
        container_id, name = line.split("\t")
        if name == container_name:
            return container_id
    return None

def run_ping_in_container(container_id, target_host, count=25):
    docker_cmd = f"docker exec {container_id} ping -c {count} {target_host}"
    try:
        result = subprocess.run(docker_cmd, shell=True, check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def extract_ping_stats(ping_output):
    rtt_values = []
    packet_loss = None

    for line in ping_output.splitlines():
        if "time=" in line:
            try:
                rtt = float(line.split("time=")[1].split()[0])
                rtt_values.append(rtt)
            except Exception as ex:
                print("RTT parse error:", ex)

    for line in ping_output.splitlines():
        if "packet loss" in line:
            try:
                # Example: "15 packets transmitted, 6 received, 60% packet loss, time 14011ms"
                packet_loss_str = line.split(",")[2].strip().split("%")[0]
                packet_loss = float(packet_loss_str)
                break
            except Exception as ex:
                print("Packet loss parse error:", ex)
    return rtt_values, packet_loss

def write_to_file(filename, data):
    with open(filename, "w") as file:
        file.write(f"{data}")

def main():
    container_name = input("Enter container name (sec or insec): ").strip()
    if container_name not in ["sec", "insec"]:
        print("Invalid container name. Please enter 'sec' or 'insec'.")
        return

    # choose host to ping
    target_host = "insec" if container_name == "sec" else "sec"

    container_id = get_container_id_by_name(container_name)
    if not container_id:
        print(f"Container '{container_name}' not found.")
        return

    print(f"Pinging {target_host} from container {container_name} ({container_id})...")
    ping_output = run_ping_in_container(container_id, target_host, count=25)
    if not ping_output:
        return

    rtt_values, packet_loss = extract_ping_stats(ping_output)
    if not rtt_values:
        print("No RTT values found in ping output.")
        return

    avg_rtt = sum(rtt_values) / len(rtt_values)
    print(f"Average RTT: {avg_rtt:.5f} ms")
    print(f"Packet Loss: {packet_loss}%")

    write_to_file("avg_rtt.txt", avg_rtt)

    with open("ping_done.txt", "w") as f:
        f.write("done")

if __name__ == '__main__':
    main()
