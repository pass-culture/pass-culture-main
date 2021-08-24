from enum import Enum
import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException as SendinblueApiException

from pcapi import settings
from pcapi.core.users import testing
from pcapi.core.users.external import UserAttributes
from pcapi.tasks.sendinblue_tasks import UpdateSendinblueContactRequest
from pcapi.tasks.sendinblue_tasks import update_contact_attributes_task


logger = logging.getLogger(__name__)


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
    USER_ID = "USER_ID"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


def update_contact_attributes(user_email: str, user_attributes: UserAttributes):
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


def format_user_attributes(user_attributes: UserAttributes) -> dict:
    return {
        SendinblueAttributes.BOOKED_OFFER_CATEGORIES.value: ",".join(user_attributes.booking_categories),
        SendinblueAttributes.BOOKED_OFFER_SUBCATEGORIES.value: ",".join(user_attributes.booking_subcategories),
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

    except SendinblueApiException as e:
        logger.exception("Exception when calling ContactsApi->create_contact: %s\n", e)
        return False
