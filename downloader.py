import threading
import time
import requests

def download_image(url):
    print(f"Starting download from {url}")
    response = requests.get(url)
    print(f"Finished downloading from {url} and the size is {len(response.content)} bytes")

urls=[
       "https://httpbin.org/image/jpeg",
       "https://httpbin.org/image/png",
        "https://httpbin.org/image/svg",
]
start=time.time()
threads = []
for url in urls:
    thread = threading.Thread(target=download_image, args=(url,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
end=time.time()
print(f"Total time taken: {end - start:.2f} seconds")
