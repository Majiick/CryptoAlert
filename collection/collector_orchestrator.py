import zmq
import pandas as pd
import threading
from data_source import continuous_data_apis
from mlogging import logger
from typing import List, Type, Dict
from data_api import Exchange, Pair
import time
from postgres_init import engine
import cryptowatch
import poloniex
import bittrex
from sqlalchemy.sql import text
from multiprocessing import Pool

COLLECT_HISTORICAL_DATA_AFTER = int(time.time())


def startup_queue():
    """
    The startup queue enqueues all commands to start/stop continuous/normal workers.
    The collector_starter listens to this channel.
    """
    context = zmq.Context()
    zmq_collector_starter_command_channel = context.socket(zmq.PUSH)
    zmq_collector_starter_command_channel.bind("tcp://0.0.0.0:5556")

    ######################################################### TEMPORARY
    # zmq_collector_starter_command_channel.send_json({'command': 'start_continuous', 'target': 'POLONIEX'})
    # for exchange_name, _ in continuous_data_apis.items():
    #     zmq_collector_starter_command_channel.send_json({'command': 'start_continuous', 'target': exchange_name})


def restart_worker(exchange_name: str):
    context = zmq.Context()
    zmq_collector_starter_command_channel = context.socket(zmq.PUSH)
    zmq_collector_starter_command_channel.bind("tcp://0.0.0.0:5556")
    zmq_collector_starter_command_channel.send_json({'command': 'restart_continuous', 'target': exchange_name})


def record_continuous_worker_interruption(exchange: str, start_time: int, end_time: int):
    # start_time: unix epoch in seconds
    # end_time: unix epoch in seconds
    assert(end_time >= start_time)
    assert(start_time > int(time.time() - 86400))  # Check if timestamp is not more than one day old
    assert(end_time > int(time.time() - 86400))  # Check if not more than one day old
    assert(type(start_time) is int)
    assert(type(end_time) is int)


    # with engine.begin() as conn:
    #     conn.execute(text(
    #         "INSERT INTO INTERRUPTION (id, start_time, end_time, exchange, fulfilled) VALUES (DEFAULT, :start_time, :end_time, :exchange, :fulfilled)"),
    #                  start_time=start_time-120,
    #                  end_time=end_time+120,
    #                  exchange=exchange,
    #                  fulfilled=False)
    #
    # logger.error('Recording continuous worker interruption: {}:{} {}'.format(start_time, end_time, exchange))


def message_rate_calculation():
    """
    This function runs on its own thread and listens in on the collector_publisher channel to calculate the rate of messages coming from each continuous worker.
    The rates are logged.
    """
    logger.info('Starting message_rate_calculation')
    context = zmq.Context()
    workers_socket = context.socket(zmq.SUB)  # Subs to collector_publisher PUB socket.
    workers_socket.connect('tcp://collector:27999')
    # We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
    # Here, the filter is the empty string, which means we receive all messages.
    # We may subscribe to several filters, thus receiving from all.
    workers_socket.setsockopt_string(zmq.SUBSCRIBE, '')

    # second_slots is used like a circular buffer with 60 entries, one entry for each second.
    # Example usage second_slots[6]['POLONIEX'] = 20. Means there were 20 messages from poloniex exchange on the 6th second.
    second_slots: Dict[int, Dict[str, int]] = dict() # Dict of second(0-59) to map of exchange name to number of messages that second.

    last_time_reported: int = int(time.time())

    while True:
        cur_second_slot: int = int(time.time()) % 60

        # Clean out the slot that comes after our current slot
        if (cur_second_slot + 1) % 60 in second_slots:
            second_slots[(cur_second_slot + 1) % 60] = dict()

        try:
            # Below line will throw exception if there's no message yet.
            json = workers_socket.recv_json(flags=zmq.NOBLOCK)  # This is a data_api.py TradeInfo JSON

            if json[0]['measurement'] == 'trade':
                exchange: str = json[0]['tags']['exchange']

                if cur_second_slot not in second_slots:
                    second_slots[cur_second_slot] = dict()

                if exchange not in second_slots[cur_second_slot]:
                    second_slots[cur_second_slot][exchange] = 0

                second_slots[cur_second_slot][exchange] += 1

        except zmq.Again as e:
            time.sleep(0.01)

        if int(time.time()) - 30 > last_time_reported:  # Report every 30 seconds
            rates: Dict[str, int] = dict()  # Exchange to total amount of messages

            for _, exchange_to_num_messages in second_slots.items():
                for exchange, num_messages in exchange_to_num_messages.items():
                    if exchange not in rates:
                        rates[exchange] = 0

                    rates[exchange] += num_messages

            logger.info('The number of trade measurements per continuous exchange in past 60 sec: ' + str(rates))

            # Check if any of the exchanges did not send any messages at all and warn if they didn't.
            # Add exchanges that are running if we didn't receive any messages from them.
            for exchange_name, _ in continuous_data_apis.items():
                if exchange_name not in rates:
                    rates[exchange_name] = 0

            for exchange, messages in rates.items():
                if messages == 0:
                    logger.error('Exchange {} had 0 messages in past 60 seconds. Sending restart command and recording interruption.'.format(exchange))
                    restart_worker(exchange)
                    record_continuous_worker_interruption(exchange, int(time.time())-60, int(time.time()))  ## TEMPORARY



            last_time_reported = int(time.time())


def collect_missing_historical_data_one_pair(pair: Pair, exchange: Exchange, start_time: int, end_time: int):
    with engine.begin() as conn:
        ohlc = cryptowatch.Cryptowatch.get_ohlc(pair, exchange, start_time, end_time, [60])
        ohlc = ohlc[60]
        # logger.debug(ohlc)
        if not ohlc:
            ohlc = cryptowatch.Cryptowatch.get_ohlc(pair.flipped(), exchange, start_time, end_time, [60])  # Flip the pair name e.g. BTCUSD to USDBTC and try again
            ohlc = ohlc[60]
            # logger.debug(ohlc)
        if ohlc:
            # for stick in ohlc:
            #     # Stick: [ CloseTime, OpenPrice, HighPrice, LowPrice, ClosePrice, Volume ]
            #     conn.execute(text("INSERT INTO OHLC (id, close_time, open_price, high_price, low_price, close_price, volume, exchange, market, time_interval) VALUES (DEFAULT, :close_time, :open_price, :high_price, :low_price, :close_price, :volume, :exchange, :market, :time_interval)"),
            #                  close_time=stick[0],
            #                  open_price=stick[1],
            #                  high_price=stick[2],
            #                  low_price=stick[3],
            #                  close_price=stick[4],
            #                  volume=stick[5],
            #                  exchange=exchange.name,
            #                  market=pair.pair,
            #                  time_interval=60)
            # return ohlc
            pass
        else:
            logger.debug('Failed to get ohlc for {} on exchange {}. start_time: {} end_time: {}'.format(pair.pair, exchange.name, start_time, end_time))
            return (pair.pair, ohlc)

        logger.debug('Collected interruption data for {} on exchange {}. start_time: {} end_time: {}'.format(pair.pair, exchange.name, start_time, end_time))
        return (pair.pair, ohlc)


def collect_missing_historical_data():
    '''
    CREATE TABLE IF NOT EXISTS INTERRUPTION(
        id SERIAL PRIMARY KEY,
        start_time BIGINT NOT NULL,
        end_time BIGINT NOT NULL,
        exchange TEXT NOT NULL,
        fulfilled BOOLEAN NOT NULL,
        times_tried INTEGER
    );
    '''
    logger.info('Starting collect_missing_historical_data')
    # Check for any missing data using the continuous worker interrupted service measure
    while True:
        logger.debug('Running collect_missing_historical_data loop.')
        with engine.begin() as conn:
            result = conn.execute(text("SELECT * FROM INTERRUPTION WHERE FULFILLED=FALSE"))

        for interruption in result:
            if interruption['exchange'] == 'BITTREX':
                pairs = bittrex.BittrexWebsockets.get_all_pairs()
            elif interruption['exchange'] == 'POLONIEX':
                pairs = poloniex.PoloniexWebsocket.get_all_pairs()
            else:
                assert(False)

            pool = Pool(150)
            args = [[p, Exchange(interruption['exchange']), int(interruption['start_time']), int(interruption['end_time'])] for p in pairs]
            logger.debug(len(pairs))
            results = pool.starmap(collect_missing_historical_data_one_pair, args)
            # logger.debug(results)
            # Results are [ (pair_name, [array of sticks]), ... ]
            with engine.begin() as conn:
                time_started = time.time()
                for result in results:
                    # result is just a (pair_name, [[ CloseTime, OpenPrice, HighPrice, LowPrice, ClosePrice, Volume ], ...])
                    pair_name = result[0]
                    for stick in result[1]:
                        conn.execute(text("INSERT INTO OHLC (id, close_time, open_price, high_price, low_price, close_price, volume, exchange, market, time_interval) VALUES (DEFAULT, :close_time, :open_price, :high_price, :low_price, :close_price, :volume, :exchange, :market, :time_interval)"),
                                     close_time=stick[0],
                                     open_price=stick[1],
                                     high_price=stick[2],
                                     low_price=stick[3],
                                     close_price=stick[4],
                                     volume=stick[5],
                                     exchange=interruption['exchange'],
                                     market=pair_name,
                                     time_interval=60)
            logger.debug("Took {} secs to write ohlc.".format(time.time() - time_started))
            with engine.begin() as conn:
                conn.execute(text("UPDATE INTERRUPTION set fulfilled=TRUE WHERE id=:id"), id=interruption['id'])

            pool.close()
            pool.join()
            time.sleep(1)

        time.sleep(1)


def listen_for_reported_interruptions():
    logger.info('Starting listen_for_reported_interruptions')

    context = zmq.Context()
    pull = context.socket(zmq.PULL)
    pull.bind('tcp://0.0.0.0:99991')

    while True:
        logger.debug('Listening for next interruption in listen_for_reported_interruptions')
        msg = pull.recv_json()
        logger.debug('listen_for_reported_interruptions received msg ' + str(msg))

        assert(msg['exchange'] is not None)
        assert(msg['start_time'] is not None)
        assert (msg['end_time'] is not None)
        record_continuous_worker_interruption(msg['exchange'], msg['start_time'], msg['end_time'])


def generate_ohlc():
    """
    CREATE TABLE IF NOT EXISTS TRADE(
      trade_time BIGINT NOT NULL,
      exchange TEXT NOT NULL,
      market TEXT NOT NULL,
      buy BOOL NOT NULL,
      price float(53) NOT NULL,
      size float(53) NOT NULL,

      PRIMARY KEY(trade_time, exchange, market, buy)
    );
    :return:
    """
    last_converted_time = time.time_ns() - 10*float('1e+9')

    '''
    Fiinsh this up. Needs to sort by market and exchange.
    '''
    return
    while True:
        with engine.begin() as conn:
            result = conn.execute(text("SELECT * FROM TRADE WHERE trade_time > :last_converted_time SORT BY trade_time ASC"), last_converted_time=last_converted_time)

        second_frame_trades = {}
        for trade in result:
            second_time = trade['trade_time'] / float('1e+9')
            if second_time not in second_frame_trades:
                second_frame_trades[second_time] = []
            second_frame_trades[second_time].append(trade)

        minute_frame_trades = {}
        for second, trades in second_frame_trades.items():
            if int(second/60) not in minute_frame_trades:
                minute_frame_trades[int(second/60)] = []
            minute_frame_trades[int(second / 60)].extend(trades)

        for minute, trades in minute_frame_trades.items():
            high = float('-inf')
            low = float('+inf')

            for trade in trades:
                if trade['price'] > high:
                    high = trade['price']

                if trade['price'] < low:
                    low = trade['price']




def main():
    message_rate_calculation_thread = threading.Thread(target=message_rate_calculation)
    message_rate_calculation_thread.start()

    collect_missing_historical_data_thread = threading.Thread(target=collect_missing_historical_data)
    collect_missing_historical_data_thread.start()

    listen_for_reported_interruptions_thread = threading.Thread(target=listen_for_reported_interruptions)
    listen_for_reported_interruptions_thread.start()

    startup_queue_thread = threading.Thread(target=startup_queue)
    startup_queue_thread.start()

    generate_ohlc_thread = threading.Thread(target=generate_ohlc)
    generate_ohlc_thread.start()

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://0.0.0.0:5557")

    for num in range(2000):
        work_message = {'num': num}
        zmq_socket.send_json(work_message)

    startup_queue_thread.join()
    message_rate_calculation_thread.join()
    collect_missing_historical_data_thread.join()
    listen_for_reported_interruptions_thread.join()
    generate_ohlc_thread.join()


if __name__ == "__main__":
    main()
