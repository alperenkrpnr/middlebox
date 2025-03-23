import asyncio
from nats.aio.client import Client as NATS
import os, random
from scapy.all import Ether

async def run():
    nc = NATS()
    nats_url = os.getenv("NATS_SURVEYOR_SERVERS", "nats://nats:4222")
    await nc.connect(nats_url)

    delays = []

    async def message_handler(msg):
        subject = msg.subject
        data = msg.data
        packet = Ether(data)
        #print(packet.show())

        delay_sec = random.expovariate(1 / 5e-6) # sec
        delay_ms = delay_sec * 1000  # ms
        delays.append(delay_ms)
        await asyncio.sleep(delay_sec)

        if subject == "inpktsec":
            await nc.publish("outpktinsec", msg.data)
        else:
            await nc.publish("outpktsec", msg.data)

        print(f"Processed a message with exponential delay {delay_ms:.5f} ms")

    await nc.subscribe("inpktsec", cb=message_handler)
    await nc.subscribe("inpktinsec", cb=message_handler)
    print("Subscribed to inpktsec and inpktinsec topics")

    while not os.path.exists("ping_done.txt"):
        await asyncio.sleep(1)

    print("Termination file detected. Disconnecting from NATS...")
    await nc.close()

    if delays:
        mean_delay = sum(delays) / len(delays)
        print(f"Mean Exponential Delay: {mean_delay:.5f} ms")
        with open("mean_delay.txt", "w") as f:
            f.write(f"{mean_delay:.5f}")
    else:
        print("No delays recorded.")

    os.remove("ping_done.txt")

if __name__ == '__main__':
    asyncio.run(run())
