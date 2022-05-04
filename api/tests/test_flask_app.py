import logging

import pytest

from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


def test_log_request_details(client, caplog):
    users_factories.BeneficiaryGrant18Factory(email="email@example.com")
    client.with_token("email@example.com")

    with caplog.at_level(logging.INFO):
        client.get(
            "/native/v1/me",
            headers={
                "device-id": "B35033A8-F7D9-4417-8A99-AC43F1ACC552",
                "request-id": "abcd",
                "X-Forwarded-For": "82.65.58.211",
            },
        )
        assert caplog.records[0].extra["deviceId"] == "B35033A8-F7D9-4417-8A99-AC43F1ACC552"
        assert caplog.records[0].extra["requestId"] == "abcd"
        assert caplog.records[0].extra["sourceIp"] == "82.65.58.211"
        assert caplog.records[0].extra["route"] == "/native/v1/me"
        assert caplog.records[0].extra["path"] == "/native/v1/me"
