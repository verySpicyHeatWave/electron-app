import queue
from flask import Flask, jsonify, Response
from flask_cors import CORS

import pika
import sys
import threading
import time

app = Flask(__name__)
CORS(app=app)

subscriber = queue.Queue(maxsize=60)
messages=[]
last_msg: 0

def get_data_callback(ch, method, properties, body):
    message = body.decode('utf-8')
    messages.append(message)
    # print(f"Received: {message}")
    try:
        subscriber.put_nowait(message)
    except queue.Full:
        print("What the fuck?! We're full!")
        while subscriber.not_empty:
            subscriber.get()
        time.sleep(1)

def consume_data():
    # print("condume_data() called")
    exchange_name = "data1"
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name,
                            exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name,
                        on_message_callback=get_data_callback,
                        auto_ack=True)

    channel.start_consuming()

# print("Starting the new thread...")
threading.Thread(target=consume_data, daemon=True).start()
# print("Started!")

@app.route("/")
def hello() -> str:
    return "Hello, world!"

@app.route('/message', methods=["GET"])
def get_message():
    print("message endpoint reached...")
    return jsonify({"This is a message from the back end!":"You did it! Yay!"})

@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(messages)

@app.route('/stream')
def stream_data():
    def event_stream():
        print("beginning event stream!")
        try:
            while True:
                try:
                    msg = subscriber.get(block=True, timeout=1.2)
                    print(f"Received: {msg}")
                    yield f"Data: {msg}\n\n"
                except queue.Empty:
                    print("What the fuck?! We're empty!")
                    yield "WHAT THE FUCK! We're empty!"
                    time.sleep(1)
        except KeyboardInterrupt:
            print("We're quitting!")

    return Response(event_stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run("localhost", 5000)
    print("we're main!")
