import json
import queue
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import pika
import threading
import time

app = Flask(__name__)
CORS(app=app)
sub_queue = queue.Queue(maxsize=20)

def send_log_flag(json_message):
    exchange_name = "log-flags"
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange_name,
                            exchange_type='fanout',
                            auto_delete=True)
    channel.basic_publish(exchange=exchange_name,
                routing_key='',
                body=json_message)
    channel.close()

def get_data_callback(ch, method, properties, body):
    message = body.decode('utf-8')
    # messages.append(message)
    try:
        sub_queue.put_nowait(message)
    except queue.Full:
        print("What the fuck?! We're full!")
        while sub_queue.not_empty:
            print(f"Deleting entry: {sub_queue.get()}")
        time.sleep(1.2)


def consume_data(exchange, event):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange,
                            exchange_type='fanout',
                            auto_delete=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name,
                        on_message_callback=get_data_callback,
                        auto_ack=True)

    while True:
        connection.process_data_events(time_limit=0)
        if event.is_set():
            break

event: threading.Event = threading.Event()
consumer = threading.Thread(target=consume_data, daemon=True, args=("nodata", event,))
consumer.start()

@app.route("/")
def hello() -> str:
    return "Hello, world!"

@app.route('/message', methods=["GET"])
def get_message():
    print("message endpoint reached...")
    return jsonify({"This is a message from the back end!":"You did it! Yay!"})

@app.route('/stream', methods=['GET'])
def stream_data():
    def event_stream():
        print("beginning event stream!")
        try:
            while True:
                try:
                    msg = sub_queue.get(block=True, timeout=1.2)
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
    send_log_flag(json.dumps(request.json))
    return request.json


@app.route('/set-exchange', methods=['POST'])
def set_exchange():
    global event
    global consumer
    exchange = str(request.json['exchange'])
    print("Setting new exchange to " + exchange)
    print(exchange)
    event.set()
    consumer.join()
    consumer = threading.Thread(target=consume_data, daemon=True, args=(exchange, event,))
    event.clear()
    consumer.start()
    return request.json


if __name__ == "__main__":
    app.run("localhost", 5000)
    print("we're main!")
