import pika
import sys
import os
import time

def callback(ch, method, properties, body):
    print(f" [x] {body}")

def main():
    exchange_name = "data1"
    if len(sys.argv) > 1:
        exchange_name = sys.argv[1]
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name,
                            exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name,
                        on_message_callback=callback,
                        auto_ack=True)

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