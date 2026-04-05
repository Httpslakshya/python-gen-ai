import asyncio
import threading
import time

def background_worker():
    while True:
        time.sleep(1)
        print("logging system health")

async def fetch_orders():
    await asyncio.sleep(3)
    print("fetched orders")

threading.Thread(target=background_worker, daemon=True).start()
asyncio.run(fetch_orders())