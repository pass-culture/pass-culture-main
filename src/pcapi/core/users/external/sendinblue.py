from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from typing import List
from typing import Optional
from typing import Union

import sib_api_v3_sdk
from sib_api_v3_sdk.api.contacts_api import ContactsApi
from sib_api_v3_sdk.rest import ApiException as SendinblueApiException

from pcapi import settings
from pcapi.core.users import testing
from pcapi.core.users.external import UserAttributes
from pcapi.tasks.sendinblue_tasks import UpdateSendinblueContactRequest
from pcapi.tasks.sendinblue_tasks import update_contact_attributes_task


logger = logging.getLogger(__name__)


@dataclass
class SendinblueUserUpdateData:
    email: str
    attributes: dict


class SendinblueAttributes(Enum):
    BOOKED_OFFER_CATEGORIES = "BOOKED_OFFER_CATEGORIES"
    BOOKED_OFFER_SUBCATEGORIES = "BOOKED_OFFER_SUBCATEGORIES"
    BOOKING_COUNT = "BOOKING_COUNT"
    CREDIT = "CREDIT"
    DATE_CREATED = "DATE_CREATED"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    DEPARTMENT_CODE = "DEPARTMENT_CODE"
    DEPOSIT_ACTIVATION_DATE = "DEPOSIT_ACTIVATION_DATE"
    DEPOSIT_EXPIRATION_DATE = "DEPOSIT_EXPIRATION_DATE"
    FIRSTNAME = "FIRSTNAME"
    HAS_COMPLETED_ID_CHECK = "HAS_COMPLETED_ID_CHECK"
    INITIAL_CREDIT = "INITIAL_CREDIT"
    IS_BENEFICIARY = "IS_BENEFICIARY"
    IS_ELIGIBLE = "IS_ELIGIBLE"
    IS_EMAIL_VALIDATED = "IS_EMAIL_VALIDATED"
    IS_PRO = "IS_PRO"
    LAST_BOOKING_DATE = "LAST_BOOKING_DATE"
    LAST_FAVORITE_CREATION_DATE = "LAST_FAVORITE_CREATION_DATE"
    LAST_VISIT_DATE = "LAST_VISIT_DATE"
    LASTNAME = "LASTNAME"
    MARKETING_EMAIL_SUBSCRIPTION = "MARKETING_EMAIL_SUBSCRIPTION"
    POSTAL_CODE = "POSTAL_CODE"
    PRODUCT_BRUT_X_USE_DATE = "PRODUCT_BRUT_X_USE_DATE"
    USER_ID = "USER_ID"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def update_contact_attributes(user_email: str, user_attributes: UserAttributes) -> None:
    formatted_attributes = format_user_attributes(user_attributes)

    constact_list_ids = (
        [settings.SENDINBLUE_PRO_CONTACT_LIST_ID]
        if user_attributes.is_pro
        else [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]
    )

    update_contact_attributes_task.delay(
        UpdateSendinblueContactRequest(
            email=user_email, attributes=formatted_attributes, contact_list_ids=constact_list_ids
        )
    )


def format_list(raw_list: List[str]) -> str:
    return ",".join(raw_list)


def format_user_attributes(user_attributes: UserAttributes) -> dict:
    return {
        SendinblueAttributes.BOOKED_OFFER_CATEGORIES.value: format_list(user_attributes.booking_categories),
        SendinblueAttributes.BOOKED_OFFER_SUBCATEGORIES.value: format_list(user_attributes.booking_subcategories),
        SendinblueAttributes.BOOKING_COUNT.value: user_attributes.booking_count,
        SendinblueAttributes.CREDIT.value: user_attributes.domains_credit.all.remaining
        if user_attributes.domains_credit
        else None,
        SendinblueAttributes.DATE_CREATED.value: user_attributes.date_created,
        SendinblueAttributes.DATE_OF_BIRTH.value: user_attributes.date_of_birth,
        SendinblueAttributes.DEPARTMENT_CODE.value: user_attributes.departement_code,
        SendinblueAttributes.DEPOSIT_ACTIVATION_DATE.value: user_attributes.deposit_activation_date,
        SendinblueAttributes.DEPOSIT_EXPIRATION_DATE.value: user_attributes.deposit_expiration_date,
        SendinblueAttributes.FIRSTNAME.value: user_attributes.first_name,
        SendinblueAttributes.HAS_COMPLETED_ID_CHECK.value: user_attributes.has_completed_id_check,
        SendinblueAttributes.INITIAL_CREDIT.value: user_attributes.domains_credit.all.initial
        if user_attributes.domains_credit
        else None,
        SendinblueAttributes.IS_BENEFICIARY.value: user_attributes.is_beneficiary,
        SendinblueAttributes.IS_ELIGIBLE.value: user_attributes.is_eligible,
        SendinblueAttributes.IS_EMAIL_VALIDATED.value: user_attributes.is_email_validated,
        SendinblueAttributes.IS_PRO.value: user_attributes.is_pro,
        SendinblueAttributes.LAST_BOOKING_DATE.value: user_attributes.last_booking_date,
        SendinblueAttributes.LAST_FAVORITE_CREATION_DATE.value: user_attributes.last_favorite_creation_date,
        SendinblueAttributes.LAST_VISIT_DATE.value: user_attributes.last_visit_date,
        SendinblueAttributes.LASTNAME.value: user_attributes.last_name,
        SendinblueAttributes.MARKETING_EMAIL_SUBSCRIPTION.value: user_attributes.marketing_email_subscription,
        SendinblueAttributes.POSTAL_CODE.value: user_attributes.postal_code,
        SendinblueAttributes.PRODUCT_BRUT_X_USE_DATE.value: user_attributes.products_use_date.get("product_brut_x_use"),
        SendinblueAttributes.USER_ID.value: user_attributes.user_id,
    }


def make_update_request(payload: UpdateSendinblueContactRequest) -> bool:
    if settings.IS_RUNNING_TESTS:
        testing.sendinblue_requests.append({"email": payload.email, "attributes": payload.attributes})
        return True

    if settings.IS_DEV:
        logger.info(
            "A request to Sendinblue Contact API would be sent for user %s with attributes %s",
            payload.email,
            payload.attributes,
        )
        return True

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    create_contact = sib_api_v3_sdk.CreateContact(
        email=payload.email,
        attributes=payload.attributes,
        list_ids=payload.contact_list_ids,
        update_enabled=True,
    )

    try:
        api_instance.create_contact(create_contact)
        return True

    except SendinblueApiException as exception:
        if exception.status == 524:
            logger.warning(
                "Timeout when calling ContactsApi->create_contact: %s",
                exception,
                extra={"email": payload.email, "attributes": payload.attributes},
            )
        else:
            logger.exception(
                "Exception when calling ContactsApi->create_contact: %s",
                exception,
                extra={"email": payload.email, "attributes": payload.attributes},
            )
        return False


def send_import_contacts_request(api_instance: ContactsApi, file_body: str, list_ids: List[int]) -> None:
    request_contact_import = sib_api_v3_sdk.RequestContactImport(
        email_blacklist=False, sms_blacklist=False, update_existing_contacts=True, empty_contacts_attributes=False
    )
    request_contact_import.file_body = file_body
    request_contact_import.list_ids = list_ids

    try:
        api_instance.import_contacts(request_contact_import)
    except SendinblueApiException as e:
        print("Exception when calling ContactsApi->import_contacts: %s" % e)


def format_file_value(value: Optional[Union[str, bool, int, datetime]]) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def build_file_body(users_data: List[SendinblueUserUpdateData]) -> str:
    """Generates a csv-like string for bulk import, based on SendinblueAttributes
       e.g.: "EMAIL;FIRSTNAME;SMS\n#john@example.com;John;Doe;31234567923"

    Args:
        users_data (List[SendinblueUserUpdateData]): users data

    Returns:
        str: corresponding csv string
    """
    file_body = ";".join(sorted(SendinblueAttributes.list())) + ";EMAIL"
    for user in users_data:
        file_body += "\n"
        file_body += ";".join([format_file_value(value) for _, value in sorted(user.attributes.items())])
        file_body += f";{user.email}"

    return file_body


def import_contacts_in_sendinblue(sendinblue_users_data: List[SendinblueUserUpdateData]) -> None:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Split users in sendinblue lists
    pro_users = [
        user_data for user_data in sendinblue_users_data if user_data.attributes[SendinblueAttributes.IS_PRO.value]
    ]
    young_users = [
        user_data for user_data in sendinblue_users_data if not user_data.attributes[SendinblueAttributes.IS_PRO.value]
    ]

    # send pro users request
    if pro_users:
        pro_users_file_body = build_file_body(pro_users)
        send_import_contacts_request(
            api_instance, file_body=pro_users_file_body, list_ids=[settings.SENDINBLUE_PRO_CONTACT_LIST_ID]
        )
    # send young users request
    if young_users:
        young_users_file_body = build_file_body(young_users)
        send_import_contacts_request(
            api_instance, file_body=young_users_file_body, list_ids=[settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]
        )
