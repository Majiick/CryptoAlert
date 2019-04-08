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


# if __name__ == '__main__':
#     import eventlet
#     from eventlet import debug
#     eventlet.monkey_patch()
#     debug.hub_blocking_detection(resolution=0.01)
# if __name__ == '__main__':
# #     from eventlet.green import zmq
# else:
import zmq
import threading
import asyncio
from aiohttp import web
import socketio
from mlogging import logger
from zmq import NOBLOCK
import multiprocessing
from multiprocessing import Process, Queue
from typing import Any
import websockets
import random
import json
import logging
from postgres_init import engine
from sqlalchemy.sql import text


logger.info("Started socketio server")


def listen_to_alert_pub(queue):
    logger.debug('Running listen_to_alert_pub')

    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
    sub_socket.connect('tcp://alert_generation:28000')
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        json = sub_socket.recv_json()
        logger.debug(json)
        queue.put(json)


if __name__ == '__main__':
    queue: Any = Queue()
    local_storage: Any = []

async def collect_queue():
    logger.debug('Running collect_queue')
    while True:
        try:
            recv_json = queue.get_nowait()
            local_storage.append(recv_json)
        except multiprocessing.queues.Empty:
            await asyncio.sleep(0.01)

async def websocket_connection(websocket, path):
    logger.debug('New websocket connection.')
    last_count_sent = 0

    interesting_events = []
    with engine.begin() as conn:
        result = conn.execute(text("SELECT * FROM INTERESTING_EVENT LIMIT 1000"))
        for row in result:
            interesting_events.append(dict(row))

    await websocket.send(json.dumps({'type': 'initial_interesting_events', 'data': interesting_events}))
    # await websocket.send(json.dumps({'type': 'initial_prices', 'data': ''}))

    while True:
        if len(local_storage) > last_count_sent:
            recv_json = local_storage[last_count_sent]
            logger.debug(recv_json)
            last_count_sent += 1

            if recv_json['measurement'] == 'latest_price':
                await websocket.send(json.dumps({'type': 'price_update', 'data': recv_json}))
            elif recv_json['measurement'] == 'alert':
                await websocket.send(json.dumps({'type': 'alert', 'data': recv_json}))
            elif recv_json['measurement'] == 'interesting_event':
                await websocket.send(json.dumps({'type': 'interesting_event', 'data': recv_json}))
            else:
                assert (False)
        else:
            await asyncio.sleep(0.01)


if __name__ == '__main__':
    p: Any = Process(target=listen_to_alert_pub, args=(queue,))
    p.start()

    start_server = websockets.serve(websocket_connection, '0.0.0.0', 8080)

    asyncio.ensure_future(collect_queue())
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    p.join()
