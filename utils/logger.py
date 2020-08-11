import logging

from utils.config import LOG_LEVEL


def configure_pc_logger():
    logging.basicConfig(format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                        level=LOG_LEVEL,
                        datefmt='%Y-%m-%d %H:%M:%S')
    _disable_werkzeug_request_logs()


def _disable_werkzeug_request_logs():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)


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
