# # import eventlet
# # eventlet.monkey_patch()
# import socketio
# import zmq
# import threading
# from aiohttp import web
# from mlogging import logger
# import asyncio
#
# logger.info("Started socketio server")
#
# app = web.Application()
# sio = socketio.AsyncServer(async_mode='aiohttp')
# sio.attach(app)
#
#
# @sio.on('connect', namespace='/price_update')
# async def connect(sid, environ):
#     logger.info("connect ", sid)
#     await sio.emit('price_update', {'data': {'msg': 'Connection established.'}}, namespace='/price_update')
#
#
# async def listen_to_alert_pub():
#     logger.debug('listen_to_alert_pub runninng.')
#
#     context = zmq.Context()
#     sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
#     sub_socket.connect('tcp://alert_generation:28000')
#     sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')
#
#     while True:
#         # TODO: Sleep 0 here might be causing big delays
#         # eventlet.sleep(0)
#         await asyncio.sleep(0.1)
#
#         try:
#             json = sub_socket.recv_json(flags=zmq.NOBLOCK)
#             logger.debug('Socketio received msg {}'.format(json))
#
#             if json['measurement'] == 'latest_price':
#                 await sio.emit('price_update', {'data': json})
#             if json['measurement'] == 'alert':
#                 await sio.emit('alert', {'data': json})
#         except zmq.Again:
#             await asyncio.sleep(0.1)
#
#
# # t = threading.Thread(target=listen_to_alert_pub)
# # t.start()
#
# async def start_background_tasks(app):
#     app['alert_pub_task'] = asyncio.create_task(listen_to_alert_pub())
#
# sio.start_background_task(listen_to_alert_pub)
# # app.on_startup.append(start_background_tasks)
# web.run_app(app)
# # sio.start_background_task(target=listen_to_alert_pub)
# # eventlet.wsgi.server(eventlet.listen(('', 443)), app)


import eventlet
eventlet.monkey_patch()
import socketio
import zmq
import threading
from aiohttp import web
from mlogging import logger

logger.info("Started socketio server")

app = web.Application()
sio = socketio.Server(async_mode='eventlet')


@sio.on('connect', namespace='/price_update')
def connect(sid, environ):
    logger.info("connect ", sid)
    sio.emit('price_update', {'data': 'Connection established.'}, namespace='/price_update')


def listen_to_alert_pub():
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
    sub_socket.connect('tcp://alert_generation:28000')
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        # TODO: Sleep 0 here might be causing big delays
        eventlet.sleep(0.1)

        try:
            json = sub_socket.recv_json(flags=zmq.NOBLOCK)

            if json['measurement'] == 'latest_price':
                sio.emit('price_update', {'data': json})
            if json['measurement'] == 'alert':
                sio.emit('alert', {'data': json})
        except zmq.Again:
            pass  # No message


# t = threading.Thread(target=listen_to_alert_pub)
# t.start()

app = socketio.Middleware(sio, app)
sio.start_background_task(target=listen_to_alert_pub)
eventlet.wsgi.server(eventlet.listen(('', 443)), app)
