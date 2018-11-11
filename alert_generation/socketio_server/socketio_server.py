import socketio
import zmq
import eventlet
from aiohttp import web

print("Started socketio server")

context = zmq.Context()
sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
sub_socket.connect('tcp://alert_generation:28000')
sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

app = web.Application()
sio = socketio.Server(async_mode='eventlet')

@sio.on('connect', namespace='/price_update')
def connect(sid, environ):
    print("connect ", sid)

app = socketio.Middleware(sio, app)
eventlet.wsgi.server(eventlet.listen(('', 8333)), app)

while True:
    json = sub_socket.recv_json()
    print(json)
