import base64
import json

from google.oauth2.service_account import Credentials
import gspread
from memoize import Memoizer

from pcapi import settings


user_spreadsheet_store = {}
memo = Memoizer(user_spreadsheet_store)


class MissingGoogleKeyException(Exception):
    pass


def get_credentials():
    google_key = settings.GOOGLE_KEY
    if not google_key:
        raise MissingGoogleKeyException()
    account_info = json.loads(base64.b64decode(google_key))
    scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    return Credentials.from_service_account_info(account_info, scopes=scopes)


@memo(max_age=60)
def get_authorized_emails_and_dept_codes():
    gc = gspread.authorize(get_credentials())
    spreadsheet = gc.open_by_key("1YCLVZNU5Gzb2P4Jaf9OW50Oedm2-Z9S099FGitFG64s")
    worksheet = spreadsheet.worksheet("Utilisateurs")

    labels = worksheet.row_values(1)
    email_index = None
    departement_index = None
    for index, label in enumerate(labels):
        if label == "Email":
            email_index = index
        elif label == "Département":
            departement_index = index
    if email_index is None:
        raise ValueError("Can't find 'Email' column in users spreadsheet")
    if departement_index is None:
        raise ValueError("Can't find 'Département' column in users spreadsheet")

    values = worksheet.get_all_values()[1:]

    return list(map(lambda v: v[email_index], values)), list(map(lambda v: v[departement_index], values))
