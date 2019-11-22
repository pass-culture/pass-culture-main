import os
import requests

SCALINGO_API_AUTH_URL = 'https://auth.scalingo.com/v1'
SCALINGO_API_APPLICATION_URL = 'https://api.scalingo.com/v1'
SCALINGO_DB_API_APPLICATION_URL = 'https://db-api.scalingo.com'


class ScalingoApiException(Exception):
    pass


def get_bearer_token(application_token: str) -> str:
    bearer_token_end_point = '/tokens/exchange'
    api_response = requests.post(f'{SCALINGO_API_AUTH_URL}{bearer_token_end_point}', auth=(None, application_token))
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['token']


def get_application_addon_id(bearer_token: str, application_name: str) -> str:
    addons_end_point = f'/apps/{application_name}/addons'
    api_response = requests.get(f'{SCALINGO_API_APPLICATION_URL}{addons_end_point}',
                                headers={'Authorization': f'Bearer {bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting addons description {api_response.content}')
    json_response = api_response.json()
    return json_response['addons'][0]['id']


def get_addon_token(bearer_token: str, application_name: str, addon_id: str) -> str:
    addon_token_end_point = f'/apps/{application_name}/addons/{addon_id}/token'
    api_response = requests.post(f'{SCALINGO_API_APPLICATION_URL}{addon_token_end_point}',
                                 headers={'Authorization': f'Bearer {bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['addon']['token']


def get_last_backup_file_identifier(db_bearer_token: str, addon_id: str) -> str:
    list_backups_end_point = f'/api/databases/{addon_id}/backups'
    api_response = requests.get(f'{SCALINGO_DB_API_APPLICATION_URL}{list_backups_end_point}',
                                headers={'Authorization': f'Bearer {db_bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['database_backups'][0]['id']


def get_download_link(db_bearer_token: str, backup_id: str, addon_id: str) -> str:
    backup_link_end_point = f'/api/databases/{addon_id}/backups/{backup_id}/archive'
    api_response = requests.get(f'{SCALINGO_DB_API_APPLICATION_URL}{backup_link_end_point}',
                                headers={'Authorization': f'Bearer {db_bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['download_url']


def get_last_backup_from_scalingo(application_name: str) -> str:
    application_token = os.environ.get('SCALINGO_TOKEN')
    bearer_token = get_bearer_token(application_token)
    addon_id = get_application_addon_id(bearer_token, application_name)
    db_bearer_token = get_addon_token(bearer_token, application_name, addon_id)
    last_backup_file_id = get_last_backup_file_identifier(db_bearer_token, addon_id)
    return get_download_link(db_bearer_token, last_backup_file_id, addon_id)
