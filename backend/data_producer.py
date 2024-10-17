import json
import pika
import random
import sys
import time


class DataProducer():
    def __init__(self, instance_name: str = "None", setv: float = 3.0):
        self.vals = {
            "battery_pn" : 0,
            "battery_sn" : 0,
            "pack_voltage" : 0,
            "pack_current" : 0,
            "cell1_voltage" : 0,
            "cell2_voltage" : 0,
            "cell3_voltage" : 0,
            "cell4_voltage" : 0,
            "cell5_voltage" : 0,
            "cell6_voltage" : 0,
            "cell7_voltage" : 0,
            "cell8_voltage" : 0,
            "pack_temp" : 0,
            "bms_temp" : 0,
            "cfet_temp" : 0,
            "dfet_temp" : 0,
            "board_temp" : 0,
            "dpo" : False
        }
        self.setv: float = setv

    def generate_data(self):
        for key in self.vals.keys():
            if key == "name": 
                continue
            self.vals[key] = self.put_variation_on_cell_voltage(self.setv)
    
    def begin_stream(self, exchange_name='data'):
        print(f"Beginning stream for {self.vals['battery_pn']} SN{self.vals['battery_sn']} on exchange {exchange_name}")
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

    def put_variation_on_cell_voltage(self, voltage):
        return round(((random.random() - 0.5) *.01 + voltage), 3)
            

if __name__ == "__main__":
    if len(sys.argv) != 5:
        exit(5)
        
    name = sys.argv[1]
    exch = sys.argv[2]
    minv = float(sys.argv[3])
    maxv = float(sys.argv[4])

    print("Starting main call...")
    producer = DataProducer(name, minv, maxv)
    producer.begin_stream(exch)
    