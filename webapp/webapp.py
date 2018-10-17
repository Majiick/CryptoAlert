from flask import Flask
import zmq
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'
