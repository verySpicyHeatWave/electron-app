import pika
import sys

message = ' '.join(sys.argv[1:]) or "Hello World!"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
channel = connection.channel()

channel.exchange_declare(exchange='logs',
                         exchange_type='fanout')

channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(f" [x] Sent {message}")
connection.close()