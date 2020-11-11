import json
import os

import gspread
from memoize import Memoizer
from oauth2client.service_account import ServiceAccountCredentials
import pygsheets
from pygsheets import Spreadsheet


user_spreadsheet_store = {}
memo = Memoizer(user_spreadsheet_store)


class MissingGoogleKeyException(Exception):
    pass


def get_credentials():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    google_key = os.environ.get("PC_GOOGLE_KEY")
    if google_key:
        google_key_json_payload = json.loads(google_key)
        key_path = "/tmp/data.json"
        with open(key_path, "w") as outfile:
            json.dump(google_key_json_payload, outfile)
        credentials = ServiceAccountCredentials.from_json_keyfile_name(key_path, scope)
        os.remove(key_path)
        return credentials
    raise MissingGoogleKeyException


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


def get_dashboard_spreadsheet() -> Spreadsheet:
    sheet_name = os.environ.get("DASHBOARD_GSHEET_NAME")
    gc = pygsheets.authorize(service_account_env_var="PC_GOOGLE_KEY")
    return gc.open(sheet_name)
