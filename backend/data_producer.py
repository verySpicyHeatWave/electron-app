import json
import pika
import random
import sys
import time


class DataProducer():
    def __init__(self, instance_name: str = "None", minv: float = 3.0, maxv: float = 4.2):
        self.vals = {
            "name" : instance_name,
            "val1" : 0,
            "val2" : 0,
            "val3" : 0,
            "val4" : 0,
            "val5" : 0,
            "val6" : 0
        }
        self.minv: float = minv
        self.maxv: float = maxv

    def generate_data(self):
        for key in self.vals.keys():
            if key == "name": 
                continue
            self.vals[key] = round(((random.random() * (self.maxv - self.minv)) + self.minv), 3)
    
    def begin_stream(self, exchange_name='data'):
        print(f"Beginning stream for {self.vals["name"]} on exchange {exchange_name}")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
        channel = connection.channel()

        channel.exchange_declare(exchange=exchange_name,
                                exchange_type='fanout')
        try:
            while True:
                time.sleep(1)
                self.generate_data()
                message = json.dumps(self.vals)
                channel.basic_publish(exchange=exchange_name,
                            routing_key='',
                            body=message)
                print(message)
        except KeyboardInterrupt:
            print(f"Killing stream for {self.vals["name"]} on exchange {exchange_name}")
            connection.close()
            

if __name__ == "__main__":
    # Just run this in three separate terminals
    # Take four arguments in: The name of the producer, the name of the exchange, the minimum value, and the maximum value.
    # Then we'll stream until I cancel it.
    if len(sys.argv) != 5:
        exit(5)
        
    name = sys.argv[1]
    exch = sys.argv[2]
    minv = float(sys.argv[3])
    maxv = float(sys.argv[4])

    print("Starting main call...")
    producer = DataProducer(name, minv, maxv)
    producer.begin_stream(exch)
    