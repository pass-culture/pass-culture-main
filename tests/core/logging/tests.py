import uuid

from pcapi.core import logging


class GetOrSetCorrelationIdTest:
    def test_request_with_no_header(self, app):
        with app.test_request_context():
            correlation_id = logging.get_or_set_correlation_id()
            assert correlation_id == ""

    def test_request_with_header(self, app):
        headers = {"X-Request-Id": uuid.uuid4().hex}
        with app.test_request_context(headers=headers):
            correlation_id = logging.get_or_set_correlation_id()
            assert correlation_id == headers["X-Request-Id"]
