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



logger.info("Started socketio server")

sio = socketio.AsyncServer(async_mode='aiohttp', logger=True, engineio_logger=True)  # logger=True, engineio_logger=True
app = web.Application()
sio.attach(app)

@sio.on('connect')
async def connect(sid, environ):
    logger.info("connect {}".format(sid))
    await sio.emit('connection_established', {'data': 'Connection established.'})


async def process_queue(queue):
    print('wtflol')
    while True:
        await sio.sleep(0.1)
        try:
            json = queue.get_nowait()
            logger.debug(json)

            if json['measurement'] == 'latest_price':
                await sio.emit('price_update', {'data': json})
            elif json['measurement'] == 'alert':
                await sio.emit('alert', {'data': json})
            elif json['measurement'] == 'interesting_event':
                await sio.emit('interesting_event', {'data': json})
            else:
                assert(False)
        except multiprocessing.queues.Empty:
            await sio.sleep(0.1)


def listen_to_alert_pub(queue):
    context = zmq.Context()
    sub_socket = context.socket(zmq.SUB)  # Subs to alert_generation pub socket
    sub_socket.connect('tcp://alert_generation:28000')
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    print('here666')
    while True:
        json = sub_socket.recv_json()
        logger.debug(json)
        queue.put(json)


# t = threading.Thread(target=listen_to_alert_pub)
# t.start()

if __name__ == '__main__':
    queue: Any = Queue()
    sio.start_background_task(process_queue, queue)
    p: Any = Process(target=listen_to_alert_pub, args=(queue,))
    p.start()

    print('here111')
    web.run_app(app)
    print('here3')
    # p.join()
    # app = web.Application()
    # app = socketio.Middleware(sio, app)
    # # debug.spew()
    # queue: Any = Queue()
    # # sio.start_background_task(target=process_queue(queue))
    # p: Any = Process(target=listen_to_alert_pub, args=(queue,))
    # p.start()
    #
    # print('here2')
    # eventlet.wsgi.server(eventlet.listen(('', 443)), app)
    # p.join()
