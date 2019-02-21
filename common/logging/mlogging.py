# This module does all of the logging for every one of the python files.
# It MUST be included since it catches and logs uncaught exceptions by overriding the exception sys hook.
import logging
import graypy
import sys
import threading

#####################################################################################################################################################################
######################################## CHANGE STD_MID_LEVEL FOR ALL PRINTS TO GO TO STDOUT ########################################################################
#####################################################################################################################################################################
#STD_MIN_LEVEL = logging.DEBUG
STD_MIN_LEVEL = logging.WARN
# STD_MIN_LEVEL = logging.ERROR


# There is a Python bug where threads do not use the sys.excepthook https://bugs.python.org/issue1230540
# I am using a work around from that thread.
init_old = threading.Thread.__init__
def init(self, *args, **kwargs):
    init_old(self, *args, **kwargs)
    run_old = self.run
    def run_with_except_hook(*args, **kw):
        try:
            run_old(*args, **kw)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            sys.excepthook(*sys.exc_info())
    self.run = run_with_except_hook
threading.Thread.__init__ = init  # type: ignore

# Override uncaught exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception


class LogFilter(logging.Filter):
    '''Filter anything above a certain level'''
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


log_filter = LogFilter(logging.WARN)
stdout_handler.setLevel(STD_MIN_LEVEL)
stdout_handler.addFilter(log_filter)
stderr_handler.setLevel(logging.WARN)

logger.addHandler(graylog_handler)
logger.addHandler(stderr_handler)
logger.addHandler(stdout_handler)

# logger.debug('Hello Graylog2.')

