from datetime import datetime
import logging
import sys

from pythonjsonlogger import jsonlogger

from pcapi.settings import LOG_LEVEL


def disable_werkzeug_request_logs() -> None:
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.ERROR)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: dict, record: logging.LogRecord, message_dict: dict) -> None:
        super().add_fields(log_record, record, message_dict)

        log_record["timestamp"] = datetime.fromtimestamp(record.__dict__.get("created")).strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        log_record["level"] = record.__dict__.get("levelname")
        log_record["from"] = "flask"


logger = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=LOG_LEVEL,
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
json_logger = logging.getLogger(__name__)


def configure_json_logger() -> None:
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomJsonFormatter("%(timestamp) %(level) %(message)")
    log_handler.setFormatter(formatter)
    json_logger.addHandler(log_handler)
    json_logger.propagate = False
