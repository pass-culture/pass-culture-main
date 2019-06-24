""" logger """
import logging

from utils.attr_dict import AttrDict
from utils.config import LOG_LEVEL

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=10,
                    datefmt='%Y-%m-%d %H:%M:%S')


# this is so that we can have log.debug(XXX) calls in the app
# without XXX being evaluated when not at debug level
# this allows args to log.debug & co. to be lambdas that will
# get called when the loglevel is right
# cf. datascience/offers, in which the data printed in
# debug calls is costly to compute.
def pc_logging(level, *args):
    global logging
    if logging.getLogger().isEnabledFor(level):
        evaled_args = map(lambda a: a() if callable(a) else a,
                          args)
        logging.log(level, *evaled_args)


logger = AttrDict()
logger.critical = lambda *args: pc_logging(logging.CRITICAL, *args)
logger.debug = lambda *args: pc_logging(logging.DEBUG, *args)
logger.error = lambda *args: pc_logging(logging.ERROR, *args)
logger.info = lambda *args: pc_logging(logging.INFO, *args)
logger.warning = lambda *args: pc_logging(logging.WARNING, *args)
