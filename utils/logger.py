import logging
from datetime import datetime

from utils.config import LOG_LEVEL
from pythonjsonlogger import jsonlogger


def disable_werkzeug_request_logs() -> None:
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)


def configure_json_logger() -> None:
    json_logger = logging.getLogger('json')

    log_handler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp) %(level) %(message)')
    log_handler.setFormatter(formatter)
    json_logger.addHandler(log_handler)
    json_logger.propagate = False


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        log_record['timestamp'] = datetime \
            .fromtimestamp(record.__dict__.get('created')) \
            .strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['level'] = record.__dict__.get('levelname')


def pc_logging(level: int, *args: str) -> None:
    if logging.getLogger().isEnabledFor(level):
        evaled_args = map(lambda a: a() if callable(a) else a, args)
        logging.log(level, *evaled_args)


class AttrDict:
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                            level=LOG_LEVEL,
                            datefmt='%Y-%m-%d %H:%M:%S')

        self.critical = lambda *args: pc_logging(logging.CRITICAL, *args)
        self.debug = lambda *args: pc_logging(logging.DEBUG, *args)
        self.error = lambda *args: pc_logging(logging.ERROR, *args)
        self.info = lambda *args: pc_logging(logging.INFO, *args)
        self.warning = lambda *args: pc_logging(logging.WARNING, *args)


logger = AttrDict()
