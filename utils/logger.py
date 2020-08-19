import logging
from datetime import datetime

from utils.config import LOG_LEVEL
from pythonjsonlogger import jsonlogger


def disable_werkzeug_request_logs():
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.ERROR)


def configure_json_logger():
    logger = logging.getLogger('json')

    logHandler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp) %(level) %(message)')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        log_record['timestamp'] = datetime.fromtimestamp(record.__dict__.get('created')).strftime(
            '%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['level'] = record.__dict__.get('levelname')
        log_record['message'] = record.__dict__.get('message')


def pc_logging(level: int, *args: str) -> None:
    if logging.getLogger().isEnabledFor(level):
        evaled_args = map(lambda a: a() if callable(a) else a, args)
        logging.log(level, *evaled_args)


class AttrDict():
    def __init__(self) -> None:
        logging.basicConfig(format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                            level=LOG_LEVEL,
                            datefmt='%Y-%m-%d %H:%M:%S')

        self.critical = lambda *args: pc_logging(logging.CRITICAL, *args)
        self.debug = lambda *args: pc_logging(logging.DEBUG, *args)
        self.error = lambda *args: pc_logging(logging.ERROR, *args)
        self.info = lambda *args: pc_logging(logging.INFO, *args)
        self.warning = lambda *args: pc_logging(logging.WARNING, *args)


logger = AttrDict()
