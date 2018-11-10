# This script is started by the collector_starter.py
# This script takes in messages from the data colleciton workers and publishes them on a channel
# It is needed since to publish you need to bind to an address and workers have multiple threads and ZeroMQ sockets can't be shared.
# So you can't create multiple sockets for each thread because the binding address will be already takes


# TODO: The workers use PUSH to push the data here. The PUSH is blocking. Need to change this no a non-blocking push type such as an interprocess queue or something else.
import zmq

def run():
    print('Running collector publisher')
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind('tcp://0.0.0.0:27999')

    pull = context.socket(zmq.PULL)
    pull.bind('tcp://0.0.0.0:27018')

    while True:
        msg = pull.recv()
        print('Collector publisher received msg ' + str(msg))
        pub.send(msg)
