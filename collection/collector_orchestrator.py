import zmq
import pandas as pd
from influxdb import DataFrameClient
import threading
from data_source import continuous_data_apis


def startup_queue():
    context = zmq.Context()
    zmq_startup_channel = context.socket(zmq.PUSH)
    zmq_startup_channel.bind("tcp://0.0.0.0:5556")

    for k, v in continuous_data_apis.items():
        zmq_startup_channel.send_json({'command': 'start_continuous', 'target': k})


def main():
    startup_queue_thread = threading.Thread(target=startup_queue)
    startup_queue_thread.start()

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://0.0.0.0:5557")

    for num in range(2000):
        work_message = {'num': num}
        zmq_socket.send_json(work_message)

    startup_queue_thread.join()

if __name__ == "__main__":
    main()
