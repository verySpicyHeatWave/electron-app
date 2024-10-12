import pika
import sys
import os
import time

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b'.') )
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))

    channel = connection.channel()
    channel.queue_declare(queue='hello')
    channel.basic_consume(queue='hello',
                        on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)