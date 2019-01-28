import logging
import graypy
import sys


class LogFilter(logging.Filter):
    def __init__(self, level):
        self.level = level

    def filter(self, record):
        return record.levelno < self.level

logger = logging.getLogger('mlogger')
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s, %(levelname)-8s [%(filename)s:%(module)s:%(funcName)s:%(lineno)d] %(message)s', datefmt='%H:%M:%S %d-%m-%Y')

# Need to enable GELF UDP in the Graylog System>Inputs as well https://stackoverflow.com/questions/28925447/python-graypy-simply-not-sending
graylog_handler = graypy.GELFHandler('graylog', 12201, level_names=True)
graylog_handler.setFormatter(formatter)
graylog_handler.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stderr_handler = logging.StreamHandler(sys.stderr)
stdout_handler.setFormatter(formatter)
stderr_handler.setFormatter(formatter)



#####################################################################################################################################################################
######################################## CHANGE STD_MID_LEVEL FOR ALL PRINTS TO GO TO STDOUT ########################################################################
#####################################################################################################################################################################
#STD_MIN_LEVEL = logging.DEBUG
STD_MIN_LEVEL = logging.WARN

log_filter = LogFilter(logging.WARN)
stdout_handler.setLevel(STD_MIN_LEVEL)
stdout_handler.addFilter(log_filter)
stderr_handler.setLevel(logging.WARN)

logger.addHandler(graylog_handler)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)

# logger.debug('Hello Graylog2.')

