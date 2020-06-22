import logging

from utils.config import LOG_LEVEL

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=LOG_LEVEL,
                    datefmt='%Y-%m-%d %H:%M:%S')


def pc_logging(level: int, *args: str) -> None:
    if logging.getLogger().isEnabledFor(level):
        evaled_args = map(lambda a: a() if callable(a) else a, args)
        logging.log(level, *evaled_args)


class AttrDict():
    def __init__(self) -> None:
        self.critical = lambda *args: pc_logging(logging.CRITICAL, *args)
        self.debug = lambda *args: pc_logging(logging.DEBUG, *args)
        self.error = lambda *args: pc_logging(logging.ERROR, *args)
        self.info = lambda *args: pc_logging(logging.INFO, *args)
        self.warning = lambda *args: pc_logging(logging.WARNING, *args)


logger = AttrDict()
