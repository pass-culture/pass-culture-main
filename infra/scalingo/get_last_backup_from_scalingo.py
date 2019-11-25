import os
import requests

SCALINGO_AUTH_URL = 'https://auth.scalingo.com/v1'
SCALINGO_API_URL = 'https://api.scalingo.com/v1'
SCALINGO_DATABASE_URL = 'https://db-api.scalingo.com'


class ScalingoApiException(Exception):
    pass


def get_application_bearer_token(application_token: str) -> str:
    bearer_token_endpoint = '/tokens/exchange'
    api_response = requests.post(f'{SCALINGO_AUTH_URL}{bearer_token_endpoint}', auth=(None, application_token))
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['token']


def get_application_addon_id(application_name: str, bearer_token: str) -> str:
    addons_endpoint = f'/apps/{application_name}/addons'
    api_response = requests.get(f'{SCALINGO_API_URL}{addons_endpoint}',
                                headers={'Authorization': f'Bearer {bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting addons description {api_response.content}')
    json_response = api_response.json()
    return json_response['addons'][0]['id']


def get_addon_token(application_name: str, addon_id: str, bearer_token: str) -> str:
    addon_token_endpoint = f'/apps/{application_name}/addons/{addon_id}/token'
    api_response = requests.post(f'{SCALINGO_API_URL}{addon_token_endpoint}',
                                 headers={'Authorization': f'Bearer {bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['addon']['token']


def get_last_backup_file_identifier(addon_id: str, db_bearer_token: str) -> str:
    list_backups_endpoint = f'/api/databases/{addon_id}/backups'
    api_response = requests.get(f'{SCALINGO_DATABASE_URL}{list_backups_endpoint}',
                                headers={'Authorization': f'Bearer {db_bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['database_backups'][0]['id']


def get_download_link(addon_id: str, backup_id: str, db_bearer_token: str) -> str:
    backup_link_endpoint = f'/api/databases/{addon_id}/backups/{backup_id}/archive'
    api_response = requests.get(f'{SCALINGO_DATABASE_URL}{backup_link_endpoint}',
                                headers={'Authorization': f'Bearer {db_bearer_token}'})
    if api_response.status_code != 200:
        raise ScalingoApiException(f'Error getting bearer token {api_response.json()}')
    json_response = api_response.json()
    return json_response['download_url']


def get_last_backup_link_from_scalingo(application_name: str) -> str:
    application_token = os.environ.get('SCALINGO_TOKEN')
    bearer_token = get_application_bearer_token(application_token)
    addon_id = get_application_addon_id(application_name, bearer_token)
    db_bearer_token = get_addon_token(application_name, addon_id, bearer_token)
    last_backup_file_id = get_last_backup_file_identifier(addon_id, db_bearer_token)
    return get_download_link(addon_id, last_backup_file_id, db_bearer_token)
