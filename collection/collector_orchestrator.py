import zmq
import pandas as pd
from influxdb import DataFrameClient
import threading
from data_source import continuous_data_apis
from mlogging import logger
from typing import List, Type, Dict
from data_api import Exchange
import time


def startup_queue():
    """
    The startup queue enqueues all commands to start/stop continuous/normal workers.
    The collector_starter listens to this channel.
    """
    context = zmq.Context()
    zmq_startup_channel = context.socket(zmq.PUSH)
    zmq_startup_channel.bind("tcp://0.0.0.0:5556")

    for exchange_name, _ in continuous_data_apis.items():
        zmq_startup_channel.send_json({'command': 'start_continuous', 'target': exchange_name})


def message_rate_calculation():
    """
    This function runs on its own thread and listens in on the collector_publisher channel to calculate the rate of messages coming from each continuous worker.
    The rates are logged.
    """
    logger.info('Starting message rate calculation')
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
        if (cur_second_slot + 1) % 5 in second_slots:
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
                    logger.warning('Exchange {} had 0 messages in past 60 seconds.'.format(exchange))

            last_time_reported = int(time.time())


def main():
    startup_queue_thread = threading.Thread(target=startup_queue)
    startup_queue_thread.start()

    message_rate_calculation_thread = threading.Thread(target=message_rate_calculation)
    message_rate_calculation_thread.start()

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://0.0.0.0:5557")

    for num in range(2000):
        work_message = {'num': num}
        zmq_socket.send_json(work_message)

    startup_queue_thread.join()
    message_rate_calculation_thread.join()

if __name__ == "__main__":
    main()
