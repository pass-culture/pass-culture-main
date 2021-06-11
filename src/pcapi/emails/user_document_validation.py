from pcapi import settings
from pcapi.core.users.models import User


class DocumentValidationUnknownError(Exception):
    pass


def build_data_for_document_verification_error(user: User, code: str) -> dict:
    error_codes_switch = {
        "unread-document": _build_unread_document_data,
        "unread-mrz-document": _build_invalid_document_data,
        "invalid-document-date": _build_invalid_document_date_data,
        "invalid-document": _build_invalid_document_data,
        "invalid-age": _build_invalid_age_data,
    }

    if code not in error_codes_switch:
        # cast to avoid an error: in case code turns out not to be a str
        raise DocumentValidationUnknownError(str(code))

    handler = error_codes_switch[code]
    return handler(user)


def _build_unread_document_data(user: User) -> dict:
    return {
        "MJ-TemplateID": 2958557,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "first_name": user.firstName,
            "url": settings.DMS_USER_URL,
        },
    }


def _build_invalid_document_date_data(user: User) -> dict:
    return {
        "MJ-TemplateID": 2958563,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "first_name": user.firstName,
            "url": settings.DMS_USER_URL,
        },
    }


def _build_invalid_document_data(user: User) -> dict:
    return {
        "MJ-TemplateID": 2958584,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "first_name": user.firstName,
        },
    }


def _build_invalid_age_data(user: User) -> dict:
    return {
        "MJ-TemplateID": 2958585,
        "MJ-TemplateLanguage": True,
        "Vars": {
            "first_name": user.firstName,
        },
    }
