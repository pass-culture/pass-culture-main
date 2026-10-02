import time
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from flask import url_for

from pcapi.connectors.google_logs import Log
from pcapi.connectors.google_logs import Severity
from pcapi.core import token as token_utils
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries

from .helpers.get import GetEndpointHelper
from .helpers.html_parser import get_soup


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]

DEFAULT_INTERVAL = 3600


class GetListLogsTest(GetEndpointHelper):
    endpoint = "backoffice.logs.list_logs"
    needed_permission = perm_models.Permissions.READ_TECH_LOGS

    # session
    expected_num_queries = 1

    def _get_search_data(self, html: str) -> dict:
        soup = get_soup(html)
        link = soup.find("tbody").find("tr").get("hx-get")
        assert link
        token = link.split("/")[-1]
        search_data = token_utils.load_token(token_utils.TokenType.LOG_SEARCH, token)
        assert search_data
        return search_data

    def test_empty_search(self, authenticated_client, clear_redis):
        before = time.time()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        after = time.time()
        search_data = self._get_search_data(response.text)
        assert search_data
        assert search_data["filters"]
        assert before < search_data["end_date"] < after
        assert search_data["start_date"] == search_data["end_date"] - DEFAULT_INTERVAL
        assert search_data["original_start_date"] == search_data["start_date"]
        assert "last_insert_id" in search_data

    def test_search_end_date(self, authenticated_client, clear_redis):

        query_args = {
            "search_type": "OFFER_CREATION",
            "search-0-search_field": "LOG_DATE",
            "search-0-operator": "LESS_THAN",
            "search-0-date": "2026-06-15",
        }
        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        search_data = self._get_search_data(response.text)
        assert search_data
        assert search_data["filters"]
        assert search_data["end_date"] == 1781481600.0
        assert search_data["start_date"] == search_data["end_date"] - DEFAULT_INTERVAL
        assert search_data["original_start_date"] == search_data["start_date"]
        assert "last_insert_id" in search_data

    def test_search_start_date(self, authenticated_client, clear_redis):
        query_args = {
            "search_type": "OFFER_CREATION",
            "search-0-search_field": "LOG_DATE",
            "search-0-operator": "GREATER_THAN_OR_EQUAL_TO",
            "search-0-date": "2026-06-15",
        }
        before = time.time()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        after = time.time()

        search_data = self._get_search_data(response.text)
        assert search_data
        assert search_data["filters"]
        assert before < search_data["end_date"] < after
        assert search_data["start_date"] == 1781481600.0
        assert search_data["original_start_date"] == search_data["start_date"]
        assert "last_insert_id" in search_data

    def test_search_offer_id(self, authenticated_client, clear_redis):
        expected_search = {
            "field": "jsonPayload.extra.offer_id",
            "operator": "=",
            "value": 12,
        }
        query_args = {
            "search_type": "OFFER_CREATION",
            "search-0-search_field": "OFFER",
            "search-0-operator": "EQUALS",
            "search-0-integer": 12,
        }

        before = time.time()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        after = time.time()
        search_data = self._get_search_data(response.text)
        assert search_data
        assert expected_search in search_data["filters"]
        assert before < search_data["end_date"] < after
        assert search_data["start_date"] == search_data["end_date"] - DEFAULT_INTERVAL
        assert search_data["original_start_date"] == search_data["start_date"]
        assert "last_insert_id" in search_data

    def test_search_product_id(self, authenticated_client, clear_redis):
        expected_search = {
            "field": "jsonPayload.extra.product_id",
            "operator": "=",
            "value": 12,
        }
        query_args = {
            "search_type": "OFFER_CREATION",
            "search-0-search_field": "PRODUCT",
            "search-0-operator": "EQUALS",
            "search-0-integer": 12,
        }

        before = time.time()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, **query_args))
            assert response.status_code == 200

        after = time.time()
        search_data = self._get_search_data(response.text)
        assert search_data
        assert expected_search in search_data["filters"]
        assert before < search_data["end_date"] < after
        assert search_data["start_date"] == search_data["end_date"] - DEFAULT_INTERVAL
        assert search_data["original_start_date"] == search_data["start_date"]
        assert "last_insert_id" in search_data


class GetListLogsRowsTest(GetEndpointHelper):
    endpoint = "backoffice.logs.list_logs_rows"
    endpoint_kwargs = {"search_token": "azerty123"}
    needed_permission = perm_models.Permissions.READ_TECH_LOGS

    # session
    # retrieve users info
    expected_num_queries = 2

    def _get_search_data(self, html: str) -> dict:
        soup = get_soup(html)
        update_element = soup.find_all("tr")[-1].find("button") or soup.find_all("tr")[-1].find("div").find("div")
        link = update_element.get("hx-get")
        assert link
        token = link.split("/")[-1]
        search_data = token_utils.load_token(token_utils.TokenType.LOG_SEARCH, token)
        assert search_data
        return token, search_data

    def test_simple_filters(self, authenticated_client, clear_redis):
        backend_mock = MagicMock()
        backend_mock.get_logs.return_value = [
            Log(
                insert_id="azert123",
                timestamp=1789999902,
                text="super important",
                user_id=None,
                impersonator_id=None,
                severity=Severity.INFO,
                extra={
                    "extra1": "value1",
                    "extra2": "value2",
                },
            )
        ]

        search_data = {
            "filters": [
                {
                    "field": "field1",
                    "operator": ">",
                    "value": "value1",
                },
                {
                    "field": "field2",
                    "operator": "<",
                    "value": "value2",
                },
            ],
            "end_date": 1790000000,
            "start_date": 1789999900,
            "original_start_date": 1789999900,
            "last_insert_id": "",
        }

        token = token_utils.create_token(token_utils.TokenType.LOG_SEARCH, search_data, ttl=10)

        with patch("pcapi.routes.backoffice.logs.blueprint.get_backend", return_value=backend_mock):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for(self.endpoint, search_token=token))
                assert response.status_code == 200

        new_token, final_search_data = self._get_search_data(response.text)
        assert final_search_data
        assert final_search_data["filters"] == search_data["filters"]
        assert final_search_data["end_date"] == search_data["start_date"]
        assert final_search_data["start_date"] == search_data["original_start_date"]
        assert final_search_data["original_start_date"] == search_data["original_start_date"]
        assert final_search_data["last_insert_id"] == "azert123"

        assert "super important" in response.text
        assert f'id="btn-{new_token}' in response.text, "pagination should be in manual"
        assert f'id="token-{token}"' in response.text
        backend_mock.get_logs.assert_called_with(
            filters='field1>"value1"\nfield2<"value2"\ntimestamp>"2026-09-21T14:11:40Z"\ntimestamp<"2026-09-21T14:13:20Z"\n',
            limit=20,
        )

    def test_auto_update(self, authenticated_client, clear_redis):
        backend_mock = MagicMock()
        backend_mock.get_logs.return_value = [
            Log(
                insert_id="azert123",
                timestamp=1789999902,
                text="super important",
                user_id=None,
                impersonator_id=None,
                severity=Severity.INFO,
                extra={
                    "extra1": "value1",
                    "extra2": "value2",
                },
            )
        ]

        search_data = {
            "filters": [
                {
                    "field": "field1",
                    "operator": ">",
                    "value": "value1",
                },
                {
                    "field": "field2",
                    "operator": "<",
                    "value": "value2",
                },
            ],
            "end_date": 1790000000,
            "start_date": 1780000000,
            "original_start_date": 1780000000,
            "last_insert_id": "",
        }

        token = token_utils.create_token(token_utils.TokenType.LOG_SEARCH, search_data, ttl=10)

        with patch("pcapi.routes.backoffice.logs.blueprint.get_backend", return_value=backend_mock):
            with assert_num_queries(self.expected_num_queries):
                response = authenticated_client.get(url_for(self.endpoint, search_token=token))
                assert response.status_code == 200

        new_token, final_search_data = self._get_search_data(response.text)
        assert final_search_data
        assert final_search_data["filters"] == search_data["filters"]
        assert final_search_data["end_date"] == 1789956800
        assert final_search_data["start_date"] == 1789956800
        assert final_search_data["original_start_date"] == search_data["original_start_date"]
        assert final_search_data["last_insert_id"] == "azert123"

        assert "super important" in response.text
        assert f'id="btn-{new_token}' not in response.text, "pagination should be in manual"
        assert f'id="token-{token}"' in response.text
        backend_mock.get_logs.assert_called_with(
            filters='field1>"value1"\nfield2<"value2"\ntimestamp>"2026-09-21T02:13:20Z"\ntimestamp<"2026-09-21T14:13:20Z"\n',
            limit=20,
        )
