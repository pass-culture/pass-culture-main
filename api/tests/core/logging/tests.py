import decimal
import enum
import json
import logging
import uuid

from flask_login import login_user
import pytest

from pcapi.core.logging import JsonFormatter
from pcapi.core.logging import get_logged_in_user_id
from pcapi.core.logging import get_or_set_correlation_id
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
                "decimal": decimal.Decimal("12.34"),
                "enum": TestingEnum.Foo,
                "exception": ValueError("Wrong frobulation factor"),
                "set": {1},
                "user": user,
                "bytes": b"encod\xc3\xa9",
            },
        )
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {
            "decimal": 12.34,
            "enum": "foo",
            "exception": "Wrong frobulation factor",
            "set": [1],
            "user": 7,
            "bytes": "encodé",
        }

        # gracefully handle non-serializable objects
        obj = object()
        record = self._make_record("Frobulated %d blobs", 12, extra={"blobs": obj})
        serialized = formatter.format(record)
        deserialized = json.loads(serialized)
        assert deserialized["message"] == "Frobulated 12 blobs"
        assert deserialized["extra"] == {"unserializable": str({"blobs": obj})}
