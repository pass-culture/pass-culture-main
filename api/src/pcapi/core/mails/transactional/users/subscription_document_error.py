from typing import Union

from pcapi.core import mails
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalEmailData
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.models.feature import FeatureToggle


class DocumentValidationUnknownError(Exception):
    pass


def send_subscription_document_error_email(email: str, code: str) -> bool:
    data = get_subscription_document_error_email_data(code)
    return mails.send(recipients=[email], data=data)


def get_subscription_document_error_email_data(code: str) -> Union[dict, SendinblueTransactionalEmailData]:

    if not FeatureToggle.ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS.is_active():
        error_codes_switch = {
            "unread-document": _get_unread_document_email_data,
            "unread-mrz-document": _get_invalid_mrz_email_data,
            "invalid-document": _get_invalid_document_email_data,
            "invalid-document-date": _get_invalid_document_date_email_data,
            "invalid-age": _get_invalid_age_email_data,
        }

        handler = error_codes_switch.get(code, _get_unread_document_email_data)
        return handler()

    error_codes_switch = {
        "information-error": TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR,
        "unread-document": TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR,
        "invalid-document": TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR,
        "unread-mrz-document": TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR,
    }

    template = error_codes_switch.get(code, TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR)
    return SendinblueTransactionalEmailData(template=template.value)


def _get_unread_document_email_data() -> dict:
    return {
        "MJ-TemplateID": 2958557,
        "MJ-TemplateLanguage": True,
        "Mj-campaign": "jouve-error-unread-document",
        "Vars": {},
    }


def _get_invalid_document_date_email_data() -> dict:
    return {
        "MJ-TemplateID": 2958563,
        "MJ-TemplateLanguage": True,
        "Mj-campaign": "jouve-error-invalid-document-date",
        "Vars": {},
    }


def _get_invalid_mrz_email_data() -> dict:
    return {
        "MJ-TemplateID": 3188025,
        "MJ-TemplateLanguage": True,
        "Mj-campaign": "jouve-error-invalid-document",
        "Vars": {},
    }


def _get_invalid_document_email_data() -> dict:
    return {
        "MJ-TemplateID": 2958584,
        "MJ-TemplateLanguage": True,
        "Mj-campaign": "jouve-error-invalid-document",
        "Vars": {},
    }


def _get_invalid_age_email_data() -> dict:
    return {
        "MJ-TemplateID": 2958585,
        "MJ-TemplateLanguage": True,
        "Mj-campaign": "jouve-error-invalid-age",
        "Vars": {},
    }
