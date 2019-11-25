from typing import Dict, List
from unittest.mock import patch, MagicMock

from infra.scalingo.get_last_backup_from_scalingo import get_last_backup_link_from_scalingo, \
    get_application_bearer_token, \
    get_addon_token, \
    get_application_addon_id, get_last_backup_file_identifier, get_download_link


@patch('os.environ.get', return_value='scalingo-token')
@patch('infra.scalingo.get_last_backup_from_scalingo.get_application_bearer_token')
@patch('infra.scalingo.get_last_backup_from_scalingo.get_application_addon_id')
@patch('infra.scalingo.get_last_backup_from_scalingo.get_addon_token')
@patch('infra.scalingo.get_last_backup_from_scalingo.get_last_backup_file_identifier')
@patch('infra.scalingo.get_last_backup_from_scalingo.get_download_link')
def test_get_last_backup_from_scalingo(mock_get_download_link,
                                       mock_get_last_backup_file_identifier,
                                       mock_get_addon_token,
                                       mock_get_application_addon_id,
                                       mock_get_application_bearer_token,
                                       mock_env_var):
    # Given
    mock_get_application_bearer_token.return_value = 'bearer-token'
    mock_get_application_addon_id.return_value = 'addon-id'
    mock_get_addon_token.return_value = 'db-bearer-token'
    mock_get_last_backup_file_identifier.return_value = 'backup-file-id'
    mock_get_download_link.return_value = 'http://backurl.com/file'

    application_name = 'application-name'

    # When
    backup_file_name = get_last_backup_link_from_scalingo(application_name)

    # Then
    assert backup_file_name == 'http://backurl.com/file'
    mock_get_application_bearer_token.assert_called_once_with('scalingo-token')
    mock_get_application_addon_id.assert_called_once_with('application-name', 'bearer-token')
    mock_get_addon_token.assert_called_once_with('application-name', 'addon-id', 'bearer-token')
    mock_get_last_backup_file_identifier.assert_called_once_with('addon-id', 'db-bearer-token')
    mock_get_download_link.assert_called_once_with('addon-id', 'backup-file-id', 'db-bearer-token')


@patch('infra.scalingo.get_last_backup_from_scalingo.requests.post')
def test_get_bearer_token(mock_request_post):
    # Given
    mock_request_post.return_value = _mock_api_response(200, [{'token': 'bearer-token'}])
    application_token = 'app-token'

    # When
    bearer_token = get_application_bearer_token(application_token)

    # Then
    mock_request_post.assert_called_once_with('https://auth.scalingo.com/v1/tokens/exchange',
                                              auth=(None, 'app-token'))
    assert bearer_token == 'bearer-token'


@patch('infra.scalingo.get_last_backup_from_scalingo.requests.get')
def test_get_addon_identifier(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [{'addons': [{'id': 'addon-id'}]}])
    bearer_token = 'bearer-token'
    application_name = 'application-name'

    # When
    addon_id = get_application_addon_id(application_name, bearer_token)

    # Then
    mock_request_get.assert_called_once_with('https://api.scalingo.com/v1/apps/application-name/addons',
                                             headers={'Authorization': 'Bearer bearer-token'})
    assert addon_id == 'addon-id'


@patch('infra.scalingo.get_last_backup_from_scalingo.requests.post')
def test_get_addon_token(mock_request_post):
    # Given
    mock_request_post.return_value = _mock_api_response(200, [{'addon': {'token': 'db-bearer-token'}}])
    bearer_token = 'bearer-token'
    application_name = 'application-name'
    addon_id = 'addon-id'

    # When
    db_bearer_token = get_addon_token(application_name, addon_id, bearer_token)

    # Then
    mock_request_post.assert_called_once_with('https://api.scalingo.com/v1/apps/application-name/addons/addon-id/token',
                                              headers={'Authorization': 'Bearer bearer-token'})
    assert db_bearer_token == 'db-bearer-token'


@patch('infra.scalingo.get_last_backup_from_scalingo.requests.get')
def test_get_last_backup_file_identifier(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [
        {'database_backups': [
            {'id': 'backup-file-id'},
            {'id': 'backup-file-id-2'}
        ]}
    ])
    db_bearer_token = 'db-bearer-token'
    addon_id = 'addon-id'

    # When
    backup_file = get_last_backup_file_identifier(addon_id, db_bearer_token)

    # Then
    mock_request_get.assert_called_once_with('https://db-api.scalingo.com/api/databases/addon-id/backups',
                                             headers={'Authorization': 'Bearer db-bearer-token'})
    assert backup_file == 'backup-file-id'


@patch('infra.scalingo.get_last_backup_from_scalingo.requests.get')
def test_get_download_link(mock_request_get):
    # Given
    mock_request_get.return_value = _mock_api_response(200, [{'download_url': 'http://backurl.com/file'}])
    db_bearer_token = 'db-bearer-token'
    addon_id = 'addon-id'
    backup_id = 'backup-id'

    # When
    backup_download_link = get_download_link(addon_id, backup_id, db_bearer_token)

    # Then
    mock_request_get.assert_called_once_with(
        'https://db-api.scalingo.com/api/databases/addon-id/backups/backup-id/archive',
        headers={'Authorization': 'Bearer db-bearer-token'})
    assert backup_download_link == 'http://backurl.com/file'


def _mock_api_response(status_code: int, ordered_return_values: List[Dict]) -> MagicMock:
    response_return_value = MagicMock(status_code=status_code, text='')
    response_return_value.json = MagicMock(side_effect=ordered_return_values)
    return response_return_value
