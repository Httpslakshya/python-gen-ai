import threading
import time

def cpu_heavy():
    print(f"crunching some numbers")
    total =0
    for i in range(10**7):
        total += i
    print("done")

start = time.time()
threads = [threading.Thread(target=cpu_heavy) for _ in range(2)]

[t.start() for t in threads]
[t.join() for t in threads]
end = time.time()
print(f"total time taken {end - start:.2f} seconds")