import logging
import graypy

print("Hello")

my_logger = logging.getLogger('test_logger')
my_logger.setLevel(logging.DEBUG)

# Need to enable GELF UDP in the Graylog System>Inputs as well https://stackoverflow.com/questions/28925447/python-graypy-simply-not-sending
handler = graypy.GELFHandler('graylog', 12201)
my_logger.addHandler(handler)

my_logger.debug('Hello Graylog2.')


def log(msg):
    print("Sending to graylog " + str(msg))
    my_logger.debug(msg)
