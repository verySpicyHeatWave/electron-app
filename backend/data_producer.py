import random
import time

MINVAL: float = 3.0
MAXVAL: float = 4.2
VALDELTA: float = MAXVAL - MINVAL

class DataProducer():
    def __init__(self):
        self.vals: dict[str, float] = {
            "val1" : 0,
            "val2" : 0,
            "val3" : 0,
            "val4" : 0,
            "val5" : 0,
            "val6" : 0
        }

    def generate_data(self):
        for key, val in self.vals.items():
            val = round(((random.random() * VALDELTA) + MINVAL), 3)
            print(f"{key}: {val}")

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