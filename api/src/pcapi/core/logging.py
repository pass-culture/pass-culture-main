import collections.abc
import contextlib
import datetime
import decimal
import enum
import json
import logging
import sys
import time
import typing
import uuid

import flask
from flask_login import current_user

from pcapi import settings


def _is_within_app_context() -> bool:
    # If we are called before setting up an application context,
    # accessing Flask global objects raise a RuntimeError.
    try:
        # Just accessing `flask.g` itself is not enough because it
        # does exist even outside an app context. We need to look
        # "inside" to trigger an exception.
        "anything" in flask.g
    except RuntimeError:
        return False
    else:
        return True


def get_or_set_correlation_id() -> str:
    """Get a correlation id (set by Nginx upstream) if we are in the
    context of an HTTP request, or get/set one from/in Flask global
    object otherwise.
    """
    if not _is_within_app_context():
        return ""
    if flask.request:
        # Our Nginx upstream should have set an HTTP header.
        return flask.request.headers.get("X-Request-Id", "")
    # XXX: the following block has not automated tests.
    try:
        return flask.g.correlation_id
    except AttributeError:
        flask.g.correlation_id = uuid.uuid4().hex
        return flask.g.correlation_id


def get_logged_in_user_id() -> int | None:
    if not _is_within_app_context():
        return None
    try:
        if not current_user:
            return None
    except AttributeError:
        # For some reason, we may get an AttributeError if this
        # function is called very soon (before some initialization is
        # done, I guess):
        #     'Flask' object has no attribute 'login_manager'
        return None
    try:
        return current_user.id
    except AttributeError:  # anonymous use
        return None


def get_api_key_offerer_id() -> int | None:
    return (
        flask.g.current_api_key.offererId
        if _is_within_app_context() and hasattr(flask.g, "current_api_key") and flask.g.current_api_key
        else None
    )


def monkey_patch_logger_makeRecord() -> None:
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):  # type: ignore [no-untyped-def]
        """Make a record but store ``extra`` arguments in an ``extra``
        attribute (not only as direct attributes of the object itself,
        like the original method does).

        Otherwise, our JsonFormatter cannot distinguish ``extra``
        arguments from regular record attributes (most of which we
        don't use).

        Note that we cannot monkey patch `logging._logRecordFactory`
        because it does not handle the ``extra`` argument.
        """
        record = self.__original_makeRecord(
            name, level, fn, lno, msg, args, exc_info, func=func, extra=extra, sinfo=sinfo
        )
        _extra = extra or {}

        # Do not keep this key in `extra` if present. It's already an
        # attribute of `record` and that's the only place we want it.
        # See also `JsonFormatter.format()`.
        _extra.pop("technical_message_id", None)
        record.extra = _extra
        return record

    logging.Logger.__original_makeRecord = logging.Logger.makeRecord  # type: ignore [attr-defined]
    logging.Logger.makeRecord = makeRecord  # type: ignore [assignment]


def monkey_patch_logger_log() -> None:
    def _log(  # type: ignore [no-untyped-def]
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
        technical_message_id=None,
    ):
        # Inject `technical_message_id` into extra, so that we can pop it
        # back in `JsonFormatter.format()` and have it at the root of
        # the log.
        extra = extra or {}
        if technical_message_id:
            extra["technical_message_id"] = technical_message_id
        return self.__original_log(
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )

    logging.Logger.__original_log = logging.Logger._log  # type: ignore [attr-defined]
    logging.Logger._log = _log  # type: ignore [assignment]


class JsonLogEncoder(json.JSONEncoder):
    def default(self, obj: typing.Any) -> str | float | list[str | float]:
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, "id"):
            return obj.id
        if isinstance(obj, bytes):
            return obj.decode("utf-8")
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        if isinstance(obj, Exception):
            return str(obj)
        return super().default(obj)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # `getattr()` is necessary for log records that have not
        # been created by our `Logger.makeRecord()` defined above.
        # It should not happen, but let's be defensive.
        extra = getattr(record, "extra", {})
        tech_msg_id = getattr(record, "technical_message_id", "")

        # We need to be able to deactivate current_user accession
        # in case we are logging inside the current_user context itself.
        user_id = None if extra.get("avoid_current_user") else get_logged_in_user_id()

        json_record = {
            "api_key_offerer_id": get_api_key_offerer_id(),
            "logging.googleapis.com/trace": get_or_set_correlation_id(),
            "module": record.name,
            "severity": record.levelname,
            "user_id": user_id,
            "message": record.getMessage(),
            "technical_message_id": tech_msg_id,
            "extra": extra,
        }
        try:
            return json.dumps(json_record, cls=JsonLogEncoder)
        except TypeError:
            # Perhaps the `extra` arguments were not serializable?
            # Let's try by dumping them as a string.
            assert _internal_logger is not None  # tell mypy it's been set
            try:
                json_record["extra"] = {"unserializable": str(extra)}
                serialized = json.dumps(json_record)
            except TypeError:
                # I don't think we can end up here. Let's be defensive, though.
                _internal_logger.exception(
                    "Could not serialize log in JSON",
                    extra={"log": str(json_record)},
                )
                return ""
            else:
                _internal_logger.exception(
                    "Could not serialize extra log arguments in JSON",
                    extra={"record": json_record, "extra": str(extra)},
                )
                return serialized


def install_logging() -> None:
    monkey_patch_logger_makeRecord()
    monkey_patch_logger_log()
    if settings.IS_DEV and not settings.IS_RUNNING_TESTS:
        # JSON is hard to read, keep the default plain text logger.
        logging.basicConfig(level=settings.LOG_LEVEL)
        _silence_noisy_loggers()

        return

    global _internal_logger  # pylint: disable=global-statement

    # Avoid side effects of calling this function more than once.
    if _internal_logger is not None:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonFormatter())
    handlers = [handler]
    # We want to log on stdout. We could choose `sys.stdout` and that
    # would work for our Kubernetes-based infrastructure... except
    # when we run `kubectl exec ... -- python`, where `sys.stdout` is
    # the (output) file descriptor of the Python process, not the file
    # descriptor of the master process (PID 1) from which logs are
    # gathered. Here we try to detect if we are running `python` like
    # this. If so, we log twice: on the standard output of the Python
    # process (so that the developer sees logs), and on the standard
    # output of the master process (for log gathering).
    if any((settings.IS_TESTING, settings.IS_STAGING, settings.IS_PROD)) and sys.stdout.isatty():
        # pylint: disable=consider-using-with
        handler2 = logging.StreamHandler(stream=open("/proc/1/fd/1", "w", encoding="utf-8"))
        handler2.setFormatter(JsonFormatter())
        handlers.append(handler2)  # type: ignore [arg-type]
    logging.basicConfig(level=settings.LOG_LEVEL, handlers=handlers, force=True)

    _internal_logger = logging.getLogger(__name__)

    _silence_noisy_loggers()


def _silence_noisy_loggers() -> None:
    logging.getLogger("spectree.config").setLevel(logging.WARNING)
    logging.getLogger("xmlschema").setLevel(logging.WARNING)
    logging.getLogger("saml2").setLevel(logging.WARNING)
    logging.getLogger("transitions").setLevel(logging.ERROR)
    logging.getLogger("gql.transport.requests").setLevel(logging.WARNING)
    # fontTools is used by weasyprint
    logging.getLogger("fontTools.subset").setLevel(logging.WARNING)

    # FIXME (dbaty, 2021-03-17): these log levels are historical.
    # Perhaps we should set them to WARNING instead?
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("rq.worker").setLevel(logging.CRITICAL)


def log_for_supervision(
    logger: logging.Logger,
    log_level: int,
    log_message: str,
    *args: typing.Any,
    **kwargs: typing.Any,
) -> None:
    logger.log(log_level, log_message, *args, **kwargs)


@contextlib.contextmanager
def log_elapsed(
    logger: logging.Logger,
    message: str,
    extra: dict | None = None,
) -> collections.abc.Generator[None, None, None]:
    """A context manager that logs ``message`` with an additional
    ``elapsed`` key in "extra" that is the execution time (in seconds)
    of the block.
    """
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    logger.info(message, extra=(extra or {}) | {"elapsed": elapsed})


# Do NOT use this logger outside of this module. It is used only to
# report errors from this module.
_internal_logger: logging.Logger | None = None
