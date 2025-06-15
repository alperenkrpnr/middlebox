import subprocess
import time
import shutil
import os

REPEATS = 10
WAIT_TIME = 20

for i in range(REPEATS):
    print(f"\nRunning experiment iteration {i+1}/{REPEATS}")

    for fname in ["features_normal.csv", "features_covert.csv", "features_mixed.csv"]:
        try:
            os.remove(f"/code/python-processor/" + fname)
        except FileNotFoundError:
            pass

    subprocess.Popen("docker exec -i sec python3 /code/sec/sender.py", shell=True)
    subprocess.Popen("docker exec -i sec python3 /code/sec/normal_sender.py", shell=True)
    subprocess.Popen("docker exec -i python-processor python3 /code/python-processor/main.py --duration 20", shell=True)

    time.sleep(WAIT_TIME + 5)

    subprocess.run("docker exec -i python-processor python3 /code/python-processor/mix.py", shell=True)

    local_name = f"features_mixed_iter{i+1}.csv"
    subprocess.run(f"docker cp python-processor:/code/python-processor/features_mixed.csv {local_name}", shell=True)

print("\nAll experiments completed. You can now run: python3 evaluate_confidence.py")
