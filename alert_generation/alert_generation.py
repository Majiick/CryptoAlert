import postgresql_init
import zmq
from price_point import PricePoint
from alert import Alert
from typing import List, Type, Dict

print("Started alert generation")

context = zmq.Context()
workers_socket = context.socket(zmq.SUB)  # Subs to collector_publisher PUB socket.
workers_socket.connect('tcp://collector:27999')
# We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
# Here, the filter is the empty string, wich means we receive all messages.
# We may subscribe to several filters, thus receiving from all.
workers_socket.setsockopt_string(zmq.SUBSCRIBE, '')

pub = context.socket(zmq.PUB)
pub.bind('tcp://0.0.0.0:28000')

while True:
    alerts: List[Alert] = []
    alerts.extend(PricePoint.get_all_from_db())
    json = workers_socket.recv_json()
    print(json)

    if json[0]['measurement'] == 'trade':
        pub.send_json({'measurement': 'latest_price', 'exchange': json[0]['tags']['exchange'], 'pair': json[0]['tags']['pair'], 'price': json[0]['fields']['price']})

        for alert in alerts:
            print(alert.__dict__)
            if alert.trigger(json[0]):
                print('pp fired off')
                pub.send_json({'measurement': 'alert', 'alert': 'price_point', 'price_point': alert.__dict__, 'trade': json[0]})


