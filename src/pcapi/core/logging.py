import json
import logging
import sys
import uuid

import flask
from flask_login import current_user

from pcapi import settings


def _is_within_app_context():
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


def get_or_set_correlation_id():
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


def get_logged_in_user_id():
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


def monkey_patch_logger_makeRecord():
    def makeRecord(self, name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None):
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
        record.extra = extra or {}
        return record

    logging.Logger.__original_makeRecord = logging.Logger.makeRecord
    logging.Logger.makeRecord = makeRecord


class JsonFormatter(logging.Formatter):
    def format(self, record):
        # `getattr()` is necessary for log records that have not
        # been created by our `Logger.makeRecord()` defined above.
        # It should not happen, but let's be defensive.
        extra = getattr(record, "extra", {})

        # We need to be able to deactivate current_user accession
        # in case we are logging inside the current_user context itself.
        user_id = None if extra.get("avoid_current_user") else get_logged_in_user_id()

        json_record = {
            "logging.googleapis.com/trace": get_or_set_correlation_id(),
            "module": record.name,
            "severity": record.levelname,
            "user_id": user_id,
            "message": record.getMessage(),
            "extra": extra,
        }
        try:
            return json.dumps(json_record)
        except TypeError:
            # Perhaps the `extra` arguments were not serializable?
            # Let's try by dumping them as a string.
            try:
                json_record["extra"] = {"unserializable": str(record.extra)}
                serialized = json.dumps(json_record)
            except TypeError:
                # I don't think we can end up here. Let's be defensive, though.
                _internal_logger.exception("Could not serialize log in JSON", extra={"log": str(json_record)})
                return ""
            else:
                _internal_logger.exception(
                    "Could not serialize extra log arguments in JSON",
                    extra={"record": json_record, "extra": str(record.extra)},
                )
                return serialized


def install_logging():
    if settings.IS_DEV and not settings.IS_RUNNING_TESTS:
        # JSON is hard to read, keep the default plain text logger.
        logging.basicConfig(level=settings.LOG_LEVEL)
        _silence_noisy_loggers()

        return

    global _internal_logger  # pylint: disable=global-statement

    # Avoid side effects of calling this function more than once.
    if _internal_logger is not None:
        return

    monkey_patch_logger_makeRecord()
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
        handler2 = logging.StreamHandler(stream=open("/proc/1/fd/1", "w"))
        handler2.setFormatter(JsonFormatter())
        handlers.append(handler2)
    logging.basicConfig(level=settings.LOG_LEVEL, handlers=handlers, force=True)

    _internal_logger = logging.getLogger(__name__)

    _silence_noisy_loggers()


def _silence_noisy_loggers():
    logging.getLogger("spectree.config").setLevel(logging.WARNING)
    # FIXME (dbaty, 2021-03-17): these log levels are historical.
    # Perhaps we should set them to WARNING instead?
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("rq.worker").setLevel(logging.CRITICAL)


# Do NOT use this logger outside of this module. It is used only to
# report errors from this module.
_internal_logger = None
