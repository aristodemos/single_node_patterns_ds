import requests
import random
import time

URL = "http://localhost:8100/work"   # change if needed

print("Starting load generator... Ctrl+C to stop")

while True:
    try:
        # random burst size
        burst = random.randint(1, 5)

        for _ in range(burst):
            try:
                requests.get(URL, timeout=1)
            except requests.exceptions.RequestException:
                pass

        # random pause
        time.sleep(random.uniform(0.1, 1.5))

    except KeyboardInterrupt:
        print("\nStopped.")
        break