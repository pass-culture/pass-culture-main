import json
import logging
import uuid

import pytest
from requests.auth import _basic_auth_str

from pcapi.core.logging import JsonFormatter
from pcapi.core.logging import get_logged_in_user_id
from pcapi.core.logging import get_or_set_correlation_id
import pcapi.core.users.factories as users_factories


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
        headers = {"Authorization": _basic_auth_str(user.email, users_factories.DEFAULT_PASSWORD)}
        with app.test_request_context(headers=headers):
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
        unserialized = json.loads(serialized)
        assert unserialized["message"] == "Frobulated 12 blobs"
        assert unserialized["extra"] == {}

        # non-empty extra
        record = self._make_record("Frobulated %d blobs", 12, extra={"blobs": 12})
        serialized = formatter.format(record)
        unserialized = json.loads(serialized)
        assert unserialized["message"] == "Frobulated 12 blobs"
        assert unserialized["extra"] == {"blobs": 12}

        # non-serializable object
        obj = object()
        record = self._make_record("Frobulated %d blobs", 12, extra={"blobs": obj})
        serialized = formatter.format(record)
        unserialized = json.loads(serialized)
        assert unserialized["message"] == "Frobulated 12 blobs"
        assert unserialized["extra"] == {"unserializable": str({"blobs": obj})}
