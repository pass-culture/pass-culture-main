from google.oauth2 import service_account


def get_credentials():
    return service_account.Credentials.from_service_account_file("credentials.json")
