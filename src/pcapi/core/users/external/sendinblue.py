import logging

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException as SendinblueApiException

from pcapi import settings
from pcapi.core.users import testing
from pcapi.core.users.external import UserAttributes
from pcapi.tasks.sendinblue_tasks import UpdateSendinblueContactRequest
from pcapi.tasks.sendinblue_tasks import update_contact_attributes_task


logger = logging.getLogger(__name__)


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
        "BOOKED_OFFER_CATEGORIES": ",".join(user_attributes.booking_categories),
        "BOOKED_OFFER_SUBCATEGORIES": ",".join(user_attributes.booking_subcategories),
        "BOOKING_COUNT": user_attributes.booking_count,
        "CREDIT": user_attributes.domains_credit.all.remaining if user_attributes.domains_credit else None,
        "DATE_CREATED": user_attributes.date_created,
        "DATE_OF_BIRTH": user_attributes.date_of_birth,
        "DEPARTMENT_CODE": user_attributes.departement_code,
        "DEPOSIT_ACTIVATION_DATE": user_attributes.deposit_activation_date,
        "DEPOSIT_EXPIRATION_DATE": user_attributes.deposit_expiration_date,
        "FIRSTNAME": user_attributes.first_name,
        "HAS_COMPLETED_ID_CHECK": user_attributes.has_completed_id_check,
        "INITIAL_CREDIT": user_attributes.domains_credit.all.initial if user_attributes.domains_credit else None,
        "IS_BENEFICIARY": user_attributes.is_beneficiary,
        "IS_ELIGIBLE": user_attributes.is_eligible,
        "IS_EMAIL_VALIDATED": user_attributes.is_email_validated,
        "IS_PRO": user_attributes.is_pro,
        "LAST_BOOKING_DATE": user_attributes.last_booking_date,
        "LAST_FAVORITE_CREATION_DATE": user_attributes.last_favorite_creation_date,
        "LAST_VISIT_DATE": user_attributes.last_visit_date,
        "LASTNAME": user_attributes.last_name,
        "MARKETING_EMAIL_SUBSCRIPTION": user_attributes.marketing_email_subscription,
        "POSTAL_CODE": user_attributes.postal_code,
        "USER_ID": user_attributes.user_id,
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
