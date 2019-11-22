from typing import Dict, List
from unittest.mock import patch, MagicMock

import os

from infra.scalingo.get_last_backup_from_scalingo import get_last_backup_from_scalingo, get_bearer_token, \
    get_addon_token, \
    get_application_addon_id, get_last_backup_file_identifier, get_download_link


@patch.dict(os.environ, {
    'SCALINGO_TOKEN_FOR_BACKUP': 'scalingo-token'
})
@patch('scripts.get_last_backup_from_scalingo.requests.post')
@patch('scripts.get_last_backup_from_scalingo.requests.get')
def test_get_last_backup_from_scalingo(mock_request_get, mock_request_post):
    # Given
    mock_request_post.return_value = _mock_api_response(200, [{'token': 'bearer-token'},
                                                              {'addon': {'token': 'db-bearer-token'}}])

    mock_request_get.return_value = _mock_api_response(200, [{'addons': [{'id': 'addon-id'}]},
                                                             {'database_backups': [{'id': 'backup-file-id'}]},
                                                             {'download_url': 'http://backurl.com/file'}])

    application_name = 'application-name'

    # When
    backup_file_name = get_last_backup_from_scalingo(application_name)

    # Then
    assert backup_file_name == 'http://backurl.com/file'


@patch('scripts.get_last_backup_from_scalingo.requests.post')
def test_get_bearer_token(mock_request_post):
    # Given
    mock_request_post.return_value = _mock_api_response(200, [{'token': 'bearer-token'}])
    application_token = 'app-token'

    # When
    bearer_token = get_bearer_token(application_token)

    # Then
    mock_request_post.assert_called_once_with('https://auth.scalingo.com/v1/tokens/exchange',
                                              auth=(None, 'app-token'))
    assert bearer_token == 'bearer-token'


@patch('scripts.get_last_backup_from_scalingo.requests.get')
def test_get_addon_identifier(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [{'addons': [{'id': 'addon-id'}]}])
    bearer_token = 'bearer-token'
    application_name = 'application-name'

    # When
    addon_id = get_application_addon_id(bearer_token, application_name)

    # Then
    mock_request_get.assert_called_once_with('https://api.scalingo.com/v1/apps/application-name/addons',
                                             headers={'Authorization': 'Bearer bearer-token'})
    assert addon_id == 'addon-id'


@patch('scripts.get_last_backup_from_scalingo.requests.post')
def test_get_addon_token(mock_request_post):
    # Given
    mock_request_post.return_value = _mock_api_response(200, [{'addon': {'token': 'db-bearer-token'}}])
    bearer_token = 'bearer-token'
    application_name = 'application-name'
    addon_id = 'addon-id'

    # When
    db_bearer_token = get_addon_token(bearer_token, application_name, addon_id)

    # Then
    mock_request_post.assert_called_once_with('https://api.scalingo.com/v1/apps/application-name/addons/addon-id/token',
                                              headers={'Authorization': 'Bearer bearer-token'})
    assert db_bearer_token == 'db-bearer-token'


@patch('scripts.get_last_backup_from_scalingo.requests.get')
def test_get_last_backup_file_identifier(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [{'database_backups': [{'id': 'backup-file-id'}]}])
    db_bearer_token = 'db-bearer-token'
    addon_id = 'addon-id'

    # When
    backup_file = get_last_backup_file_identifier(db_bearer_token, addon_id)

    # Then
    mock_request_get.assert_called_once_with('https://db-api.scalingo.com/api/databases/addon-id/backups',
                                             headers={'Authorization': 'Bearer db-bearer-token'})
    assert backup_file == 'backup-file-id'


@patch('scripts.get_last_backup_from_scalingo.requests.get')
def test_get_download_link(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [{'download_url': 'http://backurl.com/file'}])
    db_bearer_token = 'db-bearer-token'
    addon_id = 'addon-id'
    backup_id = 'backup-id'

    # When
    backup_download_link = get_download_link(db_bearer_token, backup_id, addon_id)

    # Then
    mock_request_get.assert_called_once_with(
        'https://db-api.scalingo.com/api/databases/addon-id/backups/backup-id/archive',
        headers={'Authorization': 'Bearer db-bearer-token'})
    assert backup_download_link == 'http://backurl.com/file'


def _mock_api_response(status_code: int, ordered_return_values: List[Dict]) -> MagicMock:
    response_return_value = MagicMock(status_code=status_code, text='')
    response_return_value.json = MagicMock(side_effect=ordered_return_values)
    return response_return_value
