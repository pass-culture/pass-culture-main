import logging

import pytest
from flask import url_for

from .helpers.get import GetEndpointWithoutPermissionHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class GetSaveTest(GetEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.analytics.save"

    def test_nominal(self, authenticated_client, caplog):
        event_data = {
            "name": "my super tab",
            "type": "tabClicked",
            "origin": "http://localhost:5002/pro/offer",
        }
        # When
        with caplog.at_level(logging.INFO):
            response = authenticated_client.get(url_for(self.endpoint), params=event_data)
            assert response.status_code == 200

        # Then
        assert caplog.records[0].message == "Analytics event"
        assert caplog.records[0].extra["eventOrigin"] == "backoffice_web.offer.list_offers"
        assert caplog.records[0].extra["eventName"] == event_data["name"]
        assert caplog.records[0].extra["eventType"] == event_data["type"]

    def test_invalid_data(self, authenticated_client, caplog):
        event_data = {
            "name": "my super tab",
            "origin": "http://localhost:5002/pro/offer",
        }
        # When
        with caplog.at_level(logging.INFO):
            response = authenticated_client.get(url_for(self.endpoint), params=event_data)
            assert response.status_code == 200

        # Then
        assert caplog.records[0].message == "Faulty analytics received"
        assert caplog.records[0].extra["errors"] == {"name": [], "type": ["Information obligatoire"], "origin": []}
