from multiprocessing import Process
import time
def brew_coffee():
    print("brewing the coffee")
    time.sleep(6)
    print("coffee brewed...")
if __name__ == "__main__":
    chaimaker=[Process(target=brew_coffee) for i in range(3)]
    for maker in chaimaker:
        maker.start()
    for maker in chaimaker:
        maker.join()
