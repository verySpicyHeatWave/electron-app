import queue
from flask import Flask, jsonify, Response, request
from flask_cors import CORS

import pika
import sys
import threading
import time

app = Flask(__name__)
CORS(app=app)

subscriber = queue.Queue(maxsize=5)
messages=[]
last_msg: 0

def get_data_callback(ch, method, properties, body):
    message = body.decode('utf-8')
    messages.append(message)
    try:
        subscriber.put_nowait(message)
    except queue.Full:
        print("What the fuck?! We're full!")
        while subscriber.not_empty:
            print(f"Deleting entry: {subscriber.get()}")
        time.sleep(1.2)

def consume_data():
    exchange_name = "data1"
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name,
                            exchange_type='fanout',
                            auto_delete=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name,
                        on_message_callback=get_data_callback,
                        auto_ack=True)

    channel.start_consuming()

threading.Thread(target=consume_data, daemon=True).start()

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
                    print(f"Received a good packet")
                    yield f"Data: {msg}\n\n"
                except queue.Empty:
                    print("We're not getting any data!")
                    yield "Data: TIMEOUT\n\n"
                    time.sleep(1.2)
        except KeyboardInterrupt:
            print("We're quitting!")

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/log-enable', methods=['POST'])
def toggle_logging():
    print("we got something!", request.json)
    return request.json

if __name__ == "__main__":
    app.run("localhost", 5000)
    print("we're main!")
