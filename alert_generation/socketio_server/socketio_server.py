import eventlet
eventlet.monkey_patch()
import socketio
import zmq
import threading
from aiohttp import web

print("Started socketio server")

app = web.Application()
sio = socketio.Server(async_mode='eventlet')

@sio.on('connect', namespace='/price_update')
def connect(sid, environ):
    print("connect ", sid)
    sio.emit('price_update', {'data': 'Connection established.'}, namespace='/price_update')


def listen_to_alert_pub():
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
    sub_socket.connect('tcp://alert_generation:28000')
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        # TODO: Sleep 0 here might be causing big delays
        eventlet.sleep(0)
        json = sub_socket.recv_json()
        print(json)
        if json['measurement'] == 'latest_price':
            sio.emit('price_update', {'data': json})
        if json['measurement'] == 'alert':
            sio.emit('alert', {'data': json})


# t = threading.Thread(target=listen_to_alert_pub)
# t.start()

app = socketio.Middleware(sio, app)
sio.start_background_task(target=listen_to_alert_pub)
eventlet.wsgi.server(eventlet.listen(('', 443)), app)

