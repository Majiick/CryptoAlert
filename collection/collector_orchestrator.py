import zmq
import pandas as pd
from influxdb import DataFrameClient
import threading
from data_source import continuous_data_apis
from mlogging import logger
from typing import List, Type, Dict
from data_api import Exchange
import time
import influxdb
from influxdb_init import db_client

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
    for exchange_name, _ in continuous_data_apis.items():
        zmq_collector_starter_command_channel.send_json({'command': 'start_continuous', 'target': exchange_name})


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
    write = [{
        "measurement": "continuous_interruption",
        "time": int(time.time_ns()),
        "tags": {
            "exchange": exchange,
            "fulfilled": False
        },
        "fields": {
            "pairs": "*",
            "start_time": start_time-1,  # Allow for 1 second of safety
            "end_time": end_time+1  # Allow for 1 second of safety
        }
    }]

    logger.error('Recording continuous worker interruption: ' + str(write))
    db_client.write_points(write, time_precision='n')


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
                    record_continuous_worker_interruption(exchange, int(time.time())-60, int(time.time()))

            last_time_reported = int(time.time())


def collect_missing_historical_data():
    logger.info('Starting collect_missing_historical_data')
    # Check for any missing data using the continuous worker interrupted service measure


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


def main():
    message_rate_calculation_thread = threading.Thread(target=message_rate_calculation)
    message_rate_calculation_thread.start()

    collect_missing_historical_data_thread = threading.Thread(target=collect_missing_historical_data)
    collect_missing_historical_data_thread.start()

    listen_for_reported_interruptions_thread = threading.Thread(target=listen_for_reported_interruptions)
    listen_for_reported_interruptions_thread.start()

    startup_queue_thread = threading.Thread(target=startup_queue)
    startup_queue_thread.start()

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


if __name__ == "__main__":
    main()
