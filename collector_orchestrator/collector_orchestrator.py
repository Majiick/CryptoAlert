import zmq
import pandas as pd
from influxdb import DataFrameClient

def main():
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind("tcp://0.0.0.0:5557")

    for num in range(2000):
        work_message = { 'num' : num }
        zmq_socket.send_json(work_message)

if __name__ == "__main__":
    main()
