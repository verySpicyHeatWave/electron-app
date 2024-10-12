import random
import time

MINVAL: float = 3.0
MAXVAL: float = 4.2
VALDELTA: float = MAXVAL - MINVAL

class DataProducer():
    def __init__(self):
        self.vals: list[float] = [0, 0, 0, 0, 0, 0]
    
    def generate_data(self):
        for val in self.vals:
            val = (random.random() * VALDELTA) + MINVAL
            print(val)

if __name__ == "__main__":
    producer = DataProducer()
    running: bool = True

    try:
        while running:
            print("New data's in!")
            producer.generate_data()
            print("\n========================================\n")
            time.sleep(1)
    except KeyboardInterrupt:
        running = False
        print("We're outta here!")