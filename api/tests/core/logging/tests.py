import datetime
import decimal
import enum
import json
import logging
import uuid

from flask import g
from flask_login import login_user
import pytest

from pcapi.core.logging import JsonFormatter
from pcapi.core.logging import get_logged_in_user_id
from pcapi.core.logging import get_or_set_correlation_id
from pcapi.core.logging import log_elapsed
import pcapi.core.users.factories as users_factories


class TestingEnum(enum.Enum):
    Foo = "foo"


class GetOrSetCorrelationIdTest:
    def test_request_with_no_header(self, app):
        with app.test_request_context():
            correlation_id = get_or_set_correlation_id()
            assert correlation_id == ""

    def test_request_with_header(self, app):
        headers = {"X-Request-Id": uuid.uuid4().hex}
        with app.test_request_context(headers=headers):
            correlation_id = get_or_set_correlation_id()
            assert correlation_id == headers["X-Request-Id"]


@pytest.mark.usefixtures("db_session")
class GetLoggedInUserIdTest:
    def test_request_from_anonymous_user(self, app):
        with app.test_request_context():
            user_id = get_logged_in_user_id()
            assert user_id is None

    def test_request_from_authenticated_user(self, app):
        user = users_factories.UserFactory()
        with app.test_request_context():
            login_user(user)
            user_id = get_logged_in_user_id()
            assert user_id == user.id


class JsonFormatterTest:
    def _make_record(self, message, *args, extra=None):
        logger = logging.getLogger("testing-logger")
        extra = extra or {}
        return logger.makeRecord(
            name=logger.name,
            level=logging.INFO,
            fn=None,
            lno=None,
            msg=message,
            args=args,
            exc_info=None,
            func=None,
            extra=extra,
            sinfo=None,
        )

    def test_serialization(self):
        # Sometimes, the current api key may be defined in other tests
        # and not cleaned so we need to reset it here to avoid logger
        # from accessing stale data
        g.current_api_key = None

        formatter = JsonFormatter()

        # empty extra
        record = self._make_record("Frobulated %d blobs", 12)
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {}

        # non-empty extra
        record = self._make_record("Frobulated %d blobs", 12, extra={"blobs": 12})
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {"blobs": 12}

        # use custom serializer
        user = users_factories.UserFactory.build(id=7)
        record = self._make_record(
            "Frobulated %d blobs",
            12,
            extra={
                "date": datetime.date(2020, 1, 1),
                "datetime": datetime.datetime(2020, 1, 1, 12, 0),
                "decimal": decimal.Decimal("12.34"),
                "enum": TestingEnum.Foo,
                "exception": ValueError("Wrong frobulation factor"),
                "set": {1},
                "user": user,
                "bytes": b"encod\xc3\xa9",
                "nested_complex_object": [{"foo": ["bar"]}],
            },
        )
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {
            "date": "2020-01-01",
            "datetime": "2020-01-01T12:00:00",
            "decimal": 12.34,
            "enum": "foo",
            "exception": "Wrong frobulation factor",
            "set": [1],
            "user": 7,
            "bytes": "encodé",
            "nested_complex_object": [{"foo": ["bar"]}],
        }

        # gracefully handle non-serializable objects
        obj = object()
        record = self._make_record("Frobulated %d blobs", 12, extra={"blobs": obj})
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {"unserializable": str({"blobs": obj})}


class LogElapsedTest:
    def test_log(self, caplog):
        caplog.set_level(logging.INFO)

        logger = logging.getLogger("testing-logger")
        with log_elapsed(logger, "It worked!"):
            pass
        assert "It worked!" in caplog.messages

    def test_no_log_on_exception(self, caplog):
        caplog.set_level(logging.INFO)

        def raise_exception():
            raise ValueError()

        logger = logging.getLogger("testing-logger")
        with pytest.raises(ValueError):
            with log_elapsed(logger, "It worked!"):
                raise_exception()
        assert not caplog.messages
