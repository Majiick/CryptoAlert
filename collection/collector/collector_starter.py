import zmq
import pandas as pd
import collector_publisher
from multiprocessing import Process
from typing import Type, List, Tuple, Dict
from data_api import ContinuousDataAPI
from data_source import continuous_data_apis
from mlogging import logger

started_continuous_collectors: Dict[str, Process] = {}  # Started continuous collectors and their process.


def main():
    # Start the collector_publisher
    p = Process(target=collector_publisher.run)
    p.start()

    context = zmq.Context()

    collector_starter_command_channel = context.socket(zmq.PULL)
    collector_starter_command_channel.connect("tcp://collector-orchestrator:5556")

    while True:
        command = collector_starter_command_channel.recv_json()
        logger.info('collector_starter received new command {}'.format(command))

        if command['command'] == 'start_continuous':
            assert(command['target'] in continuous_data_apis)
            assert(command['target'] not in started_continuous_collectors)
            continuous_data_api_type: Type[ContinuousDataAPI] = continuous_data_apis[command['target']]
            continuous_data_api = continuous_data_api_type(continuous_data_api_type.get_all_pairs())

            p = Process(target=continuous_data_api.run_blocking)
            p.start()
            started_continuous_collectors[command['target']] = p

        if command['command'] == 'restart_continuous':
            assert(command['target'] in continuous_data_apis)
            assert(command['target'] in started_continuous_collectors)
            logger.debug('Collector starter received restart_continuous for {}. Recreating.'.format(command['target']))

            process = started_continuous_collectors[command['target']]
            logger.debug('Continuous worker {} is_alive: {}'.format(command['target'], process.is_alive()))
            logger.debug('Continuous worker {} exitcode(None if still running): {}'.format(command['target'], process.exitcode))
            process.kill()

            # Recreate
            continuous_data_api_type: Type[ContinuousDataAPI] = continuous_data_apis[command['target']]
            continuous_data_api = continuous_data_api_type(continuous_data_api_type.get_all_pairs())
            p = Process(target=continuous_data_api.run_blocking)
            p.start()
            started_continuous_collectors[command['target']] = p
            logger.debug('Continuous worker {} recreated.'.format(command['target']))


if __name__ == "__main__":
    main()
