import pika
import sys

message = ' '.join(sys.argv[1:]) or "Hello World!"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))

channel = connection.channel()
channel.queue_declare(queue='hello')

channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=message)
connection.close()