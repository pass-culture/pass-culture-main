import json
from io import StringIO
from unittest import mock

import pytest
import requests_mock
from algoliasearch.search_index import SearchIndex

import pcapi.core.search.commands.settings as commands_settings
from pcapi import settings


class AlgoliaSettingsTest:
    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_get_an_index_client_from_index_name(self, index_type):
        client = commands_settings._get_index_client(index_type)

        assert isinstance(client, SearchIndex)
        assert client.name == index_type.value
        assert client.app_id == settings.ALGOLIA_APPLICATION_ID

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_retrieve_settings_from_algolia(self, index_type):
        index = commands_settings._get_index_client(index_type)
        index_settings = {"random_field": "random_value"}

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=index_settings,
                complete_qs=False,
            )

            outputs = commands_settings._get_settings(index)

        assert requests_mocker.called_once
        assert len(outputs) == 1
        assert json.dumps(index_settings, indent=4) in outputs

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_send_settings_to_algolia(self, index_type):
        index = commands_settings._get_index_client(index_type)
        config_path = commands_settings._get_index_default_file(index_type)
        old_index_settings = {"random_field": "random_value"}
        config_file_content = {"random_field": "other_value"}

        with (
            requests_mock.Mocker() as requests_mocker,
            mock.patch("builtins.open", return_value=StringIO(json.dumps(config_file_content, indent=4))) as mock_open,
        ):
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=old_index_settings,
                complete_qs=False,
            )
            requests_mocker.register_uri(
                "PUT",
                f"https://{index.app_id}.algolia.net/1/indexes/{index.name}/settings",
                json={
                    "updatedAt": "2013-08-21T13:20:18.960Z",
                    "taskID": 10210332,
                },
                complete_qs=False,
            )

            outputs = commands_settings._set_settings(index, config_path, not_dry=True)

        assert requests_mocker.call_count == 2
        mock_open.assert_called_once_with(commands_settings._get_index_default_file(index_type), "r", encoding="utf-8")
        put_request = requests_mocker.request_history[1]
        assert put_request.text == json.dumps(config_file_content)
        assert len(outputs) == 1  # diff

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_set_settings_without_replicas(self, index_type):
        index = commands_settings._get_index_client(index_type)
        config_path = commands_settings._get_index_default_file(index_type)
        # replicas is present in file but not in current config -> will not be applied
        old_index_settings = {"random_field": "random_value"}
        config_file_content = {"replicas": ["my_replica"], "random_field": "other_value"}

        with (
            requests_mock.Mocker() as requests_mocker,
            mock.patch("builtins.open", return_value=StringIO(json.dumps(config_file_content, indent=4))) as mock_open,
        ):
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=old_index_settings,
                complete_qs=False,
            )
            requests_mocker.register_uri(
                "PUT",
                f"https://{index.app_id}.algolia.net/1/indexes/{index.name}/settings",
                json={"updatedAt": "2013-08-21T13:20:18.960Z", "taskID": 10210332},
                complete_qs=False,
            )

            outputs = commands_settings._set_settings(index, config_path, not_dry=True)

        assert requests_mocker.call_count == 2
        mock_open.assert_called_once_with(commands_settings._get_index_default_file(index_type), "r", encoding="utf-8")
        put_request = requests_mocker.request_history[1]
        assert put_request.text == json.dumps(
            {key: value for key, value in config_file_content.items() if key != "replicas"}
        )
        assert len(outputs) == 1  # diff

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_set_settings_with_replicas(self, index_type):
        index = commands_settings._get_index_client(index_type)
        config_path = commands_settings._get_index_default_file(index_type)
        # replicas is present in file and in current config -> will be applied
        old_index_settings = {"replicas": ["my_replica"], "random_field": "random_value"}
        config_file_content = {"replicas": ["my_new_replica"], "random_field": "other_value"}

        with (
            requests_mock.Mocker() as requests_mocker,
            mock.patch("builtins.open", return_value=StringIO(json.dumps(config_file_content, indent=4))) as mock_open,
        ):
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=old_index_settings,
                complete_qs=False,
            )
            requests_mocker.register_uri(
                "PUT",
                f"https://{index.app_id}.algolia.net/1/indexes/{index.name}/settings",
                json={"updatedAt": "2013-08-21T13:20:18.960Z", "taskID": 10210332},
                complete_qs=False,
            )

            outputs = commands_settings._set_settings(index, config_path, not_dry=True)

        assert requests_mocker.call_count == 2
        mock_open.assert_called_once_with(commands_settings._get_index_default_file(index_type), "r", encoding="utf-8")
        put_request = requests_mocker.request_history[1]
        assert put_request.text == json.dumps(config_file_content)
        assert len(outputs) == 1  # diff

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_dry_settings_retrieval_actually_does_nothing(self, index_type):
        index = commands_settings._get_index_client(index_type)

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                complete_qs=False,
            )
            requests_mocker.register_uri(
                "PUT",
                f"https://{index.app_id}.algolia.net/1/indexes/{index.name}/settings",
                complete_qs=False,
            )

            outputs = commands_settings._get_settings(index, not_dry=False)

        assert not requests_mocker.called
        assert len(outputs) == 2  # dry sim messages: settings fetched + settings displayed
        assert index_type.value in outputs[0]
        assert index_type.value in outputs[1]

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_dry_settings_applying_actually_does_nothing(self, index_type):
        index = commands_settings._get_index_client(index_type)
        config_path = commands_settings._get_index_default_file(index_type)
        old_index_settings = {"random_field": "random_value"}
        config_file_content = {"random_field": "other_value"}

        with (
            requests_mock.Mocker() as requests_mocker,
            mock.patch("builtins.open", return_value=StringIO(json.dumps(config_file_content, indent=4))) as mock_open,
        ):
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=old_index_settings,
                complete_qs=False,
            )
            requests_mocker.register_uri(
                "PUT",
                f"https://{index.app_id}.algolia.net/1/indexes/{index.name}/settings",
                complete_qs=False,
            )

            outputs = commands_settings._set_settings(
                index,
                config_path,
                not_dry=False,
            )

        # GET was called but not PUT
        assert requests_mocker.call_count == 1
        assert requests_mocker.request_history[0].method == "GET"

        mock_open.assert_called_once_with(commands_settings._get_index_default_file(index_type), "r", encoding="utf-8")
        assert len(outputs) == 3
        assert outputs[0] == f"settings will be read from {config_path}"
        assert outputs[1] == f"settings will be applied to {index_type.value} Algolia index"
        assert outputs[2] == commands_settings._get_dict_diff(old_index_settings, config_file_content)
        assert '"random_field": "random_value"' in outputs[2] and '"random_field": "other_value"' in outputs[2]
