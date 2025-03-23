import matplotlib.pyplot as plt

def read_value_from_file(filename):
    try:
        with open(filename, "r") as f:
            value = float(f.read().strip())
        return value
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def main():
    mean_delay = read_value_from_file("mean_delay.txt")
    avg_rtt = read_value_from_file("avg_rtt.txt")

    if mean_delay is None or avg_rtt is None:
        print("Could not read necessary data for plotting.")
        return

    plt.figure()
    
    plt.scatter(mean_delay, avg_rtt, s=100, color='blue')
    
    plt.xlabel("Mean Random Delay (ms)")
    plt.ylabel("Average RTT (ms)")
    plt.title("Mean Random Delay vs Average RTT")
    plt.grid(True)

    plt.axvline(x=mean_delay, color='r', linestyle='--')
    plt.axhline(y=avg_rtt, color='r', linestyle='--')

    plt.savefig("plot.png")
    plt.show()

if __name__ == '__main__':
    main()
