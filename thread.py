import threading
import time

def water_boiled():
    print("bolling the water")
    time.sleep(6)
    print("maggie boiled...")
    
def maggie ():
    time.sleep(2)
    print("adding magie to boiled water")
    
def masala():
    time.sleep(4)
    print("adding masala to out maggie")
SamaySuru=time.time()
maggie1 = threading.Thread(target=water_boiled)
maggie2 = threading.Thread(target=maggie)
maggie3 = threading.Thread(target=masala)

maggie1.start()
maggie2.start()
maggie3.start()

maggie1.join()
maggie2.join()
maggie3.join()
SamayKhatam=time.time()

print(f"total time taken {SamayKhatam - SamaySuru:.2f} seconds")
