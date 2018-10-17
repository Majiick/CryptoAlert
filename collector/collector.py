import zmq
import pandas as pd
from influxdb import DataFrameClient

def main():
    context = zmq.Context()

    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect("tcp://collector-orchestrator:5557")

    while True:
        work = consumer_receiver.recv_json()
        data = work['num']
        print(data)

if __name__ == "__main__":
    main()
