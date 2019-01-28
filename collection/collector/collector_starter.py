import zmq
import pandas as pd
import collector_publisher
from influxdb import DataFrameClient
from multiprocessing import Process
from typing import Type
from data_api import ContinuousDataAPI
from data_source import continuous_data_apis
from mlogging import logger


def main():
    # Start the collector_publisher
    p = Process(target=collector_publisher.run)
    p.start()

    context = zmq.Context()

    startup_channel = context.socket(zmq.PULL)
    startup_channel.connect("tcp://collector-orchestrator:5556")

    processes = []
    while True:
        command = startup_channel.recv_json()
        logger.info('collector_starter received new command {}'.format(command))

        if command['command'] == 'start_continuous':
            assert(command['target'] in continuous_data_apis)
            continuous_data_api_type: Type[ContinuousDataAPI] = continuous_data_apis[command['target']]
            continuous_data_api = continuous_data_api_type(continuous_data_api_type.get_all_pairs())

            p = Process(target=continuous_data_api.run_blocking)
            p.start()
            processes.append(p)

if __name__ == "__main__":
    main()
