import postgresql_init
import zmq
from price_point import PricePoint
from alert import Alert
from typing import List, Type, Dict
from mlogging import logger
from email_notification import EmailNotification

logger.info("Started alert generation")
last_trade_price : Dict[str, Dict[str, float]] = {}  # Dict[Exchange, Dict[Pair, Last Trade Price]]

context = zmq.Context()
workers_socket = context.socket(zmq.SUB)  # Subs to collector_publisher PUB socket.
workers_socket.connect('tcp://collector:27999')
# We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
# Here, the filter is the empty string, which means we receive all messages.
# We may subscribe to several filters, thus receiving from all.
workers_socket.setsockopt_string(zmq.SUBSCRIBE, '')

pub_socketio_channel = context.socket(zmq.PUB)
pub_socketio_channel.bind('tcp://0.0.0.0:28000')

while True:
    alerts: List[Alert] = []
    alerts.extend(PricePoint.get_all_from_db())
    json = workers_socket.recv_json()  # This is a data_api.py TradeInfo JSON
    logger.debug('Alert generation received new point: ' + str(json))

    if json[0]['measurement'] == 'trade':
        pub_socketio_channel.send_json({'measurement': 'latest_price', 'exchange': json[0]['tags']['exchange'], 'pair': json[0]['tags']['pair'], 'price': json[0]['fields']['price']})

        # Set last_trade_price
        if json[0]['tags']['exchange'] not in last_trade_price:
            last_trade_price[json[0]['tags']['exchange']] = {}

        last_trade_price[json[0]['tags']['exchange']][json[0]['tags']['pair']] = json[0]['fields']['price']

        for exchange, pairs in last_trade_price.items():
            for pair in pairs:
                for other_exchange, _ in last_trade_price.items():
                    if other_exchange != exchange:
                        if pair in last_trade_price[other_exchange]:
                            print('Price difference for {}: {}'.format(pair, abs(last_trade_price[exchange][pair] - last_trade_price[other_exchange][pair])))
                            print('Price for {} at {} is {}. While at {} it is {}.'.format(pair, exchange, last_trade_price[exchange][pair], other_exchange, last_trade_price[other_exchange][pair]))


        for alert in alerts:
            logger.debug(alert.__dict__)
            if not alert.fulfilled or alert.repeat:
                if alert.trigger(json[0]):
                    notifications = EmailNotification.get_all_from_db(alert.alert_pk)
                    for notification in notifications:
                        notification.notify()

                    logger.info('pp fired off')
                    pub_socketio_channel.send_json({'measurement': 'alert', 'alert': 'price_point', 'price_point': alert.__dict__, 'trade': json[0]})
                    alert.mark_fulfilled()


