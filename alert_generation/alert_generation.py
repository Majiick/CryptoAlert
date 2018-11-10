import zmq

print("Started alert generation")

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://collector:27999")
# We must declare the socket as of type SUBSCRIBER, and pass a prefix filter.
# Here, the filter is the empty string, wich means we receive all messages.
# We may subscribe to several filters, thus receiving from all.
socket.setsockopt_string(zmq.SUBSCRIBE, '')

while True:
    json = socket.recv()
    print(json)
