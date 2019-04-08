import postgresql_init
import zmq
from price_point import PricePoint
from volume_point import VolumePoint
from price_percentage import PricePercentage
from alert import Alert
from typing import List, Type, Dict, Any
from mlogging import logger
from email_notification import EmailNotification
from postgresql_init import engine
from sqlalchemy.sql import text
import time


def calculate_volume(pair: str, exchange: str):
    """
    Returns a [5 second, 10 second, 30 second, 1 minute, 10 minute and 30 minute volume]
    """
    ret = []

    time_started_selects = time.time()
    with engine.begin() as conn:
        for time_frame in [5, 10, 30, 1*60, 10*60, 30*60]:
            result = conn.execute(text(
                "SELECT sum(size) FROM TRADE WHERE trade_time > (extract(epoch from now()) * 1000000000) - cast(1 as bigint)*:time_frame*1000000000 AND market=:market AND exchange=:exchange;"),
                                  time_frame=int(time_frame),
                                  market=pair,
                                  exchange=exchange)
            result = result.fetchone()
            if result[0] is None:
                logger.warning('No result for volume query for {}'.format(pair, exchange))
                ret.append(0)
            else:
                ret.append(result[0])

    # logger.debug("Time to select: {}".format(time.time() - time_started_selects))
    # logger.debug("{} {} {}".format(exchange, pair, ret))
    return ret


def write_interesting_event_to_db(event):
    '''
    CREATE TABLE IF NOT EXISTS INTERESTING_EVENT(
      id SERIAL PRIMARY KEY,
      event_time BIGINT NOT NULL,
      exchange TEXT NOT NULL,
      market TEXT NOT NULL,
      message TEXT NOT NULL,
      event_type TEXT NOT NULL
    );
    '''

    assert('event_time' in event)
    assert('exchange' in event)
    assert('market' in event)
    assert('message' in event)
    assert('event_type' in event)
    with engine.begin() as conn:
        s = text(
            "insert into INTERESTING_EVENT (event_time, exchange, market, message, event_type) values (:event_time, :exchange, :market, :message, :event_type)")
        conn.execute(s, event_time=event['event_time'], exchange=event['exchange'], market=event['market'], message=event['message'], event_type=event['event_type'])

# https://www.calculatorsoup.com/calculators/algebra/percent-difference-calculator.php
def percentage_difference(v1, v2):
    return abs(v1 - v2) / ((v1 + v2)/2.0) * 100

logger.info("Started alert generation")
last_trade_price: Dict[str, Dict[str, float]] = {}  # Dict[Exchange, Dict[Pair, Last Trade Price]]
placed_orders: Any = []  # List[(time_placed, pair, exchange, price, other_exchange_price), ...]

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
    alerts.extend(VolumePoint.get_all_from_db())
    alerts.extend(PricePercentage.get_all_from_db())
    json = workers_socket.recv_json()  # This is a data_api.py TradeInfo JSON
    logger.debug('Alert generation received new point: ' + str(json))

    if json[0]['measurement'] == 'trade':
        pub_socketio_channel.send_json({'measurement': 'latest_price', 'exchange': json[0]['tags']['exchange'], 'pair': json[0]['tags']['pair'], 'price': json[0]['fields']['price']})

        # Set last_trade_price
        if json[0]['tags']['exchange'] not in last_trade_price:
            last_trade_price[json[0]['tags']['exchange']] = {}

        last_trade_price[json[0]['tags']['exchange']][json[0]['tags']['pair']] = json[0]['fields']['price']

        for placed_order in placed_orders:
            if time.time() - 60 > placed_order[0]:
                logger.info('Executing placed order {}. Last trade price on exchange is {}. Profit: {}'.format(placed_order, last_trade_price[placed_order[2]][placed_order[1]], last_trade_price[placed_order[2]][placed_order[1]] - placed_order[3]))
        placed_orders = [x for x in placed_orders if not time.time() - 60 > x[0]]

        for exchange, pairs in last_trade_price.items():
            for pair in pairs:
                for other_exchange, _ in last_trade_price.items():
                    if other_exchange != exchange:
                        if pair in last_trade_price[other_exchange]:
                            # https://www.calculatorsoup.com/calculators/algebra/percent-difference-calculator.php
                            price_difference = abs(last_trade_price[exchange][pair] - last_trade_price[other_exchange][pair]) / ((last_trade_price[exchange][pair] + last_trade_price[other_exchange][pair])/2.0) * 100

                            if price_difference > 0.01:
                                skip = False
                                for plcord in placed_orders:
                                    if plcord[1] == pair:
                                        skip = True
                                if not skip:
                                    exchange_volumes = calculate_volume(pair, exchange)
                                    other_exchange_volumes = calculate_volume(pair, other_exchange)

                                    # logger.debug(exchange_volumes[5])
                                    # logger.debug(other_exchange_volumes[5])
                                    # logger.debug('Volume percentage difference for {} is {}'.format(pair, percentage_difference(exchange_volumes[5], other_exchange_volumes[5])))
                                    if exchange_volumes[5] > other_exchange_volumes[5]:
                                        diff = last_trade_price[exchange][pair] - last_trade_price[other_exchange][pair]
                                        # logger.debug('Volume higher at {}'.format(exchange))
                                        if diff > 0:
                                            placed_orders.append((time.time(), pair, other_exchange, last_trade_price[other_exchange][pair], last_trade_price[exchange][pair]))
                                            # logger.debug('placed order {}'.format(placed_orders[-1]))
                                    else:
                                        diff = last_trade_price[other_exchange][pair] - last_trade_price[exchange][pair]
                                        # logger.debug('Volume higher at {}'.format(other_exchange))
                                        if diff > 0:
                                            placed_orders.append((time.time(), pair, exchange, last_trade_price[exchange][pair], last_trade_price[other_exchange][pair]))
                                            # logger.debug('placed order {}'.format(placed_orders[-1]))
                                    # logger.info('Price difference percentage for {}: {}'.format(pair, price_difference))
                                    # logger.info('Price difference for {}: {}'.format(pair, abs(last_trade_price[exchange][pair] - last_trade_price[other_exchange][pair])))
                                    # logger.info('Price for {} at {} is {}. While at {} it is {}.'.format(pair, exchange, last_trade_price[exchange][pair], other_exchange, last_trade_price[other_exchange][pair]))
                                    # pub_socketio_channel.send_json({'measurement': 'interesting_event', 'message': 'Price for {} at {} is {}. While at {} it is {}.'.format(pair, exchange, last_trade_price[exchange][pair], other_exchange, last_trade_price[other_exchange][pair])})
                            else:
                                # logger.debug('{} {}'.format(pair, price_difference))
                                pass


        for alert in alerts:
            logger.debug(alert.__dict__)
            if not alert.fulfilled or alert.repeat:
                if alert.trigger(json[0]):
                    notifications = EmailNotification.get_all_from_db(alert.alert_pk)
                    for notification in notifications:
                        notification.notify()

                    logger.info('pp fired off {} {}. On trade {}'.format(type(alert), alert.__dict__, json))
                    if not alert.broadcast_interesting_event_on_trigger:
                        pub_socketio_channel.send_json({'measurement': 'alert', 'alert_type': alert.alert_type, 'alert': alert.__dict__, 'trade': json[0], 'event_description': alert.get_interesting_event_description()})
                    if not alert.repeat:
                        alert.mark_fulfilled()
                    if alert.broadcast_interesting_event_on_trigger:
                        interesting_event = alert.get_interesting_event_description()
                        write_interesting_event_to_db(interesting_event)
                        interesting_event['measurement'] = 'interesting_event'
                        logger.debug(interesting_event)
                        pub_socketio_channel.send_json(interesting_event)


