import logging
import graypy

print("Hello")

my_logger = logging.getLogger('test_logger')
my_logger.setLevel(logging.DEBUG)

handler = graypy.GELFHandler('graylog', 9000)
my_logger.addHandler(handler)

my_logger.debug('Hello Graylog2.')