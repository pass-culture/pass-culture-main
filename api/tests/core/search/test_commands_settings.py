from io import StringIO
import json
from unittest import mock

from algoliasearch.search_index import SearchIndex
import pytest
import requests_mock

from pcapi import settings
import pcapi.core.search.commands.settings as commands_settings


class AlgoliaSettingsTest:
    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_get_an_index_client_from_index_name(self, index_type):
        # when
        client = commands_settings._get_index_client(index_type)

        # then
        assert isinstance(client, SearchIndex)
        assert client.name == index_type.value
        assert client.app_id == settings.ALGOLIA_APPLICATION_ID

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_retrieve_settings_from_algolia(self, index_type):
        # given
        index = commands_settings._get_index_client(index_type)
        index_settings = {"random_field": "random_value"}

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.register_uri(
                "GET",
                f"https://{index.app_id}-dsn.algolia.net/1/indexes/{index.name}/settings",
                json=index_settings,
                complete_qs=False,
            )

            # when
            outputs = commands_settings._get_settings(index)

        # then
        assert requests_mocker.called_once
        assert len(outputs) == 1
        assert json.dumps(index_settings, indent=4) in outputs

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_can_send_settings_to_algolia(self, index_type):
        # given
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

            # when
            outputs = commands_settings._set_settings(index, config_path, dry=False)

        # then
        assert requests_mocker.call_count == 2
        assert mock_open.call_once_with(commands_settings._get_index_default_file(index_type), "r")
        put_request = requests_mocker.request_history[1]
        assert put_request.text == json.dumps(config_file_content)
        assert len(outputs) == 1  # diff

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_dry_settings_retrieval_actually_does_nothing(self, index_type):
        # given
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

            # when
            outputs = commands_settings._get_settings(index, dry=True)

        # then
        assert not requests_mocker.called
        assert len(outputs) == 2  # dry sim messages: settings fetched + settings displayed
        assert index_type.value in outputs[0]
        assert index_type.value in outputs[1]

    @pytest.mark.parametrize("index_type", list(commands_settings.IndexTypes))
    def test_dry_settings_applying_actually_does_nothing(self, index_type):
        # given
        index = commands_settings._get_index_client(index_type)
        config_path = commands_settings._get_index_default_file(index_type)

        with (
            requests_mock.Mocker() as requests_mocker,
            mock.patch("builtins.open", return_value=StringIO("")) as mock_open,
        ):
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

            # when
            outputs = commands_settings._set_settings(
                index,
                config_path,
                dry=True,
            )

        # then
        assert not requests_mocker.called
        assert not mock_open.called
        # dry sim messages: settings fetched + settings displayed + settings read + settings applied
        assert len(outputs) == 2
        assert config_path in outputs[0]
        assert index_type.value in outputs[1]
