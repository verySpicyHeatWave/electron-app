from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app=app)

@app.route("/")
def hello() -> str:
    return "Hello, world!"

@app.route('/brian')
def hello_brian():
    return 'You know my name already!'

@app.route('/message', methods=["GET"])
def get_message():
    print("message endpoint reached...")
    return jsonify({"This is a message from the back end!":"You did it! Yay!"})

@app.route('/brian/<special>')
def hello_special(special):
    return f"Well isn't that just fucking {special}"

if __name__ == "__main__":
    app.run("localhost", 6969)