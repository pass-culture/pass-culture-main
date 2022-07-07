from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from itertools import islice
import json
import logging
from time import sleep
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.api.contacts_api import ContactsApi
from sib_api_v3_sdk.api.process_api import ProcessApi
from sib_api_v3_sdk.models.created_process_id import CreatedProcessId
from sib_api_v3_sdk.models.get_process import GetProcess
from sib_api_v3_sdk.models.post_contact_info import PostContactInfo
from sib_api_v3_sdk.rest import ApiException as SendinblueApiException
import urllib3.exceptions

from pcapi import settings
from pcapi.core.users import testing
from pcapi.core.users.external import ProAttributes
from pcapi.core.users.external import UserAttributes
from pcapi.core.users.models import UserRole
from pcapi.models.api_errors import ApiErrors
from pcapi.tasks.sendinblue_tasks import update_contact_attributes_task
from pcapi.tasks.serialization.sendinblue_tasks import UpdateSendinblueContactRequest


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
    DMS_APPLICATION_APPROVED = "DMS_APPLICATION_APPROVED"
    DMS_APPLICATION_SUBMITTED = "DMS_APPLICATION_SUBMITTED"
    ELIGIBILITY = "ELIGIBILITY"
    FIRSTNAME = "FIRSTNAME"
    HAS_BOOKINGS = "HAS_BOOKINGS"
    HAS_COMPLETED_ID_CHECK = "HAS_COMPLETED_ID_CHECK"
    HAS_OFFERS = "HAS_OFFERS"
    INITIAL_CREDIT = "INITIAL_CREDIT"
    IS_BENEFICIARY = "IS_BENEFICIARY"
    IS_BENEFICIARY_18 = "IS_BENEFICIARY_18"
    IS_BOOKING_EMAIL = "IS_BOOKING_EMAIL"
    IS_CURRENT_BENEFICIARY = "IS_CURRENT_BENEFICIARY"
    IS_FORMER_BENEFICIARY = "IS_FORMER_BENEFICIARY"
    IS_ELIGIBLE = "IS_ELIGIBLE"
    IS_EMAIL_VALIDATED = "IS_EMAIL_VALIDATED"
    IS_PERMANENT = "IS_PERMANENT"
    IS_PRO = "IS_PRO"
    IS_UNDERAGE_BENEFICIARY = "IS_UNDERAGE_BENEFICIARY"
    IS_USER_EMAIL = "IS_USER_EMAIL"
    IS_VIRTUAL = "IS_VIRTUAL"
    LAST_BOOKING_DATE = "LAST_BOOKING_DATE"
    LAST_FAVORITE_CREATION_DATE = "LAST_FAVORITE_CREATION_DATE"
    LAST_VISIT_DATE = "LAST_VISIT_DATE"
    LASTNAME = "LASTNAME"
    MARKETING_EMAIL_SUBSCRIPTION = "MARKETING_EMAIL_SUBSCRIPTION"
    MOST_BOOKED_OFFER_SUBCATEGORY = "MOST_BOOKED_OFFER_SUBCATEGORY"
    OFFERER_NAME = "OFFERER_NAME"
    POSTAL_CODE = "POSTAL_CODE"
    PRODUCT_BRUT_X_USE_DATE = "PRODUCT_BRUT_X_USE_DATE"
    USER_ID = "USER_ID"
    USER_IS_ATTACHED = "USER_IS_ATTACHED"
    USER_IS_CREATOR = "USER_IS_CREATOR"
    VENUE_COUNT = "VENUE_COUNT"
    VENUE_LABEL = "VENUE_LABEL"
    VENUE_NAME = "VENUE_NAME"
    VENUE_TYPE = "VENUE_TYPE"
    IS_EAC = "IS_EAC"

    @classmethod
    def list(cls):  # type: ignore [no-untyped-def]
        return list(map(lambda c: c.value, cls))


def update_contact_attributes(
    user_email: str, attributes: UserAttributes | ProAttributes, asynchronous: bool = True
) -> None:
    formatted_attributes = format_user_attributes(attributes)

    contact_list_ids = (
        [settings.SENDINBLUE_PRO_CONTACT_LIST_ID] if attributes.is_pro else [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]
    )

    contact_request = UpdateSendinblueContactRequest(
        email=user_email,
        attributes=formatted_attributes,
        contact_list_ids=contact_list_ids,
        emailBlacklisted=(not attributes.marketing_email_subscription),  # attribute may be None
    )

    if asynchronous:
        update_contact_attributes_task.delay(contact_request)
    else:
        if not make_update_request(contact_request):
            raise ApiErrors()


def format_list(raw_list: Iterable[str]) -> str:
    return ",".join(raw_list)


def format_list_or_str(raw_value: str | Iterable[str]) -> str:
    if isinstance(raw_value, str):
        return raw_value
    return format_list(raw_value)


def _get_attr(attributes: UserAttributes | ProAttributes, name: str, func: Callable[[Any], Any] = None) -> Any:
    value = getattr(attributes, name, None)
    if value is not None and func is not None:
        value = func(value)
    return value


def format_user_attributes(attributes: UserAttributes | ProAttributes) -> dict:
    return {
        SendinblueAttributes.BOOKED_OFFER_CATEGORIES.value: _get_attr(attributes, "booking_categories", format_list),
        SendinblueAttributes.BOOKED_OFFER_SUBCATEGORIES.value: _get_attr(
            attributes, "booking_subcategories", format_list
        ),
        SendinblueAttributes.BOOKING_COUNT.value: _get_attr(attributes, "booking_count"),
        SendinblueAttributes.CREDIT.value: _get_attr(attributes, "domains_credit", lambda v: v.all.remaining),
        SendinblueAttributes.DATE_CREATED.value: _get_attr(attributes, "date_created"),
        SendinblueAttributes.DATE_OF_BIRTH.value: _get_attr(attributes, "date_of_birth"),
        SendinblueAttributes.DEPARTMENT_CODE.value: _get_attr(attributes, "departement_code", format_list_or_str),
        SendinblueAttributes.DEPOSIT_ACTIVATION_DATE.value: _get_attr(attributes, "deposit_activation_date"),
        SendinblueAttributes.DEPOSIT_EXPIRATION_DATE.value: _get_attr(attributes, "deposit_expiration_date"),
        SendinblueAttributes.DMS_APPLICATION_APPROVED.value: _get_attr(attributes, "dms_application_approved"),
        SendinblueAttributes.DMS_APPLICATION_SUBMITTED.value: _get_attr(attributes, "dms_application_submitted"),
        SendinblueAttributes.ELIGIBILITY.value: _get_attr(attributes, "eligibility"),
        SendinblueAttributes.FIRSTNAME.value: _get_attr(attributes, "first_name"),
        SendinblueAttributes.HAS_BOOKINGS.value: _get_attr(attributes, "has_bookings"),
        SendinblueAttributes.HAS_COMPLETED_ID_CHECK.value: _get_attr(attributes, "has_completed_id_check"),
        SendinblueAttributes.HAS_OFFERS.value: _get_attr(attributes, "has_offers"),
        SendinblueAttributes.INITIAL_CREDIT.value: _get_attr(attributes, "domains_credit", lambda v: v.all.initial),
        SendinblueAttributes.IS_BENEFICIARY.value: _get_attr(attributes, "is_beneficiary"),
        SendinblueAttributes.IS_BENEFICIARY_18.value: _get_attr(
            attributes, "roles", lambda v: UserRole.BENEFICIARY.value in v
        ),
        SendinblueAttributes.IS_BOOKING_EMAIL.value: _get_attr(attributes, "is_booking_email"),
        SendinblueAttributes.IS_CURRENT_BENEFICIARY.value: _get_attr(attributes, "is_current_beneficiary"),
        SendinblueAttributes.IS_FORMER_BENEFICIARY.value: _get_attr(attributes, "is_former_beneficiary"),
        SendinblueAttributes.IS_ELIGIBLE.value: _get_attr(attributes, "is_eligible"),
        SendinblueAttributes.IS_EMAIL_VALIDATED.value: _get_attr(attributes, "is_email_validated"),
        SendinblueAttributes.IS_PERMANENT.value: _get_attr(attributes, "isPermanent"),
        SendinblueAttributes.IS_PRO.value: _get_attr(attributes, "is_pro"),
        SendinblueAttributes.IS_UNDERAGE_BENEFICIARY.value: _get_attr(
            attributes, "roles", lambda v: UserRole.UNDERAGE_BENEFICIARY.value in v
        ),
        SendinblueAttributes.IS_USER_EMAIL.value: _get_attr(attributes, "is_user_email"),
        SendinblueAttributes.IS_VIRTUAL.value: _get_attr(attributes, "isVirtual"),
        SendinblueAttributes.LAST_BOOKING_DATE.value: _get_attr(attributes, "last_booking_date"),
        SendinblueAttributes.LAST_FAVORITE_CREATION_DATE.value: _get_attr(attributes, "last_favorite_creation_date"),
        SendinblueAttributes.LAST_VISIT_DATE.value: _get_attr(attributes, "last_visit_date"),
        SendinblueAttributes.LASTNAME.value: _get_attr(attributes, "last_name"),
        SendinblueAttributes.MARKETING_EMAIL_SUBSCRIPTION.value: _get_attr(attributes, "marketing_email_subscription"),
        SendinblueAttributes.MOST_BOOKED_OFFER_SUBCATEGORY.value: _get_attr(attributes, "most_booked_subcategory"),
        SendinblueAttributes.OFFERER_NAME.value: _get_attr(attributes, "offerers_names", format_list),
        SendinblueAttributes.POSTAL_CODE.value: _get_attr(attributes, "postal_code", format_list_or_str),
        SendinblueAttributes.PRODUCT_BRUT_X_USE_DATE.value: _get_attr(
            attributes, "products_use_date", lambda v: v.get("product_brut_x_use")
        ),
        SendinblueAttributes.USER_ID.value: _get_attr(attributes, "user_id"),
        SendinblueAttributes.USER_IS_ATTACHED.value: _get_attr(attributes, "user_is_attached"),
        SendinblueAttributes.USER_IS_CREATOR.value: _get_attr(attributes, "user_is_creator"),
        SendinblueAttributes.VENUE_COUNT.value: _get_attr(attributes, "venues_ids", len),
        SendinblueAttributes.VENUE_LABEL.value: _get_attr(attributes, "venues_labels", format_list),
        SendinblueAttributes.VENUE_NAME.value: _get_attr(attributes, "venues_names", format_list),
        SendinblueAttributes.VENUE_TYPE.value: _get_attr(attributes, "venues_types", format_list),
        SendinblueAttributes.IS_EAC.value: _get_attr(attributes, "is_eac"),
    }


def make_update_request(payload: UpdateSendinblueContactRequest) -> bool:
    if settings.IS_RUNNING_TESTS:
        testing.sendinblue_requests.append(
            {"email": payload.email, "attributes": payload.attributes, "emailBlacklisted": payload.emailBlacklisted}
        )
        return True

    if settings.IS_DEV:
        logger.info(
            "A request to Sendinblue Contact API would be sent for user %s with attributes %s emailBlacklisted: %s",
            payload.email,
            payload.attributes,
            payload.emailBlacklisted,
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
        email_blacklisted=payload.emailBlacklisted,
    )

    try:
        api_instance.create_contact(create_contact)
        return True

    except SendinblueApiException as exception:
        if exception.status == 524:
            logger.exception(
                "Timeout when calling ContactsApi->create_contact",
                extra={
                    "email": payload.email,
                    "attributes": payload.attributes,
                    "emailBlacklisted": payload.emailBlacklisted,
                },
            )
        else:
            logger.exception(  # pylint: disable=logging-fstring-interpolation
                f"Exception when calling ContactsApi->create_contact with status={exception.status}",
                extra={
                    "email": payload.email,
                    "attributes": payload.attributes,
                    "emailBlacklisted": payload.emailBlacklisted,
                },
            )
        return False

    except Exception:  # pylint: disable=broad-except
        logger.exception(
            "Exception when calling ContactsApi->create_contact",
            extra={
                "email": payload.email,
                "attributes": payload.attributes,
                "emailBlacklisted": payload.emailBlacklisted,
            },
        )
        return False


def send_import_contacts_request(
    api_instance: ContactsApi, file_body: str, list_ids: list[int], email_blacklist: bool = False
) -> None:
    request_contact_import = sib_api_v3_sdk.RequestContactImport(
        email_blacklist=email_blacklist,
        sms_blacklist=False,
        update_existing_contacts=True,
        empty_contacts_attributes=False,
    )
    request_contact_import.file_body = file_body
    request_contact_import.list_ids = list_ids

    try:
        api_instance.import_contacts(request_contact_import)
    except SendinblueApiException as e:
        logger.exception("Exception when calling ContactsApi->import_contacts: %s", e)


def format_file_value(value: Optional[str | bool | int | datetime]) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def build_file_body(users_data: list[SendinblueUserUpdateData]) -> str:
    """Generates a csv-like string for bulk import, based on SendinblueAttributes
       e.g.: "EMAIL;FIRSTNAME;SMS\n#john@example.com;John;Doe;31234567923"

    Args:
        users_data (list[SendinblueUserUpdateData]): users data

    Returns:
        str: corresponding csv string
    """
    file_body = ";".join(sorted(SendinblueAttributes.list())) + ";EMAIL"
    for user in users_data:
        file_body += "\n"
        file_body += ";".join([format_file_value(value) for _, value in sorted(user.attributes.items())])
        file_body += f";{user.email}"

    return file_body


def import_contacts_in_sendinblue(
    sendinblue_users_data: list[SendinblueUserUpdateData], email_blacklist: bool = False
) -> None:
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
            api_instance,
            file_body=pro_users_file_body,
            list_ids=[settings.SENDINBLUE_PRO_CONTACT_LIST_ID],
            email_blacklist=email_blacklist,
        )
    # send young users request
    if young_users:
        young_users_file_body = build_file_body(young_users)
        send_import_contacts_request(
            api_instance,
            file_body=young_users_file_body,
            list_ids=[settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID],
            email_blacklist=email_blacklist,
        )


def _wait_for_process(api_instance: ProcessApi, process_id: int) -> bool:
    seconds = 0
    # Last status should be 'completed' (exhaustive list of statuses not given in sendinblue API documentation)
    status = "queued"
    while status in ("queued", "in_process") and seconds < 3600:
        if not settings.IS_RUNNING_TESTS:
            sleep(1)
        try:
            api_response: GetProcess = api_instance.get_process(process_id)
        except urllib3.exceptions.HTTPError:
            pass
        else:
            logger.info("ProcessApi->get_process(%d) returned: %s", process_id, api_response)
            status = api_response.status
        seconds += 1

    return status == "completed"


def _send_import_request(api_instance: ContactsApi, sib_list_id: int, count: int, file_body: str) -> int:
    request_contact_import = sib_api_v3_sdk.RequestContactImport()
    request_contact_import.file_body = file_body
    request_contact_import.list_ids = [sib_list_id]

    logger.info("ContactsApi->import_contacts: %d emails, size: %d KB", count, len(file_body) / 1024)

    import_response: CreatedProcessId = api_instance.import_contacts(request_contact_import)
    logger.info("ContactsApi->import_contacts(%d) returned: %s", sib_list_id, import_response)

    return import_response.process_id


def add_contacts_to_list(user_emails: Iterable[str], sib_list_id: int, clear_list_first: bool = False) -> bool:
    """
    Fills in a list of contacts using Sendinblue API.
    This function is intended to be used for automation and returns synchronously (waits for completion).

    Args:
        user_emails (Iterable[str]): list or generator of matching user email addresses
        sib_list_id (int): Sendinblue list identifier
        clear_list_first (bool): clear all contacts from the list before adding emails

    Returns:
        bool: True when successful, False otherwise
    """

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
    contacts_api_instance: ContactsApi = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(configuration))
    process_api_instance: ProcessApi = sib_api_v3_sdk.ProcessApi(sib_api_v3_sdk.ApiClient(configuration))

    if clear_list_first:
        # https://developers.sendinblue.com/reference/removecontactfromlist
        remove_contact = sib_api_v3_sdk.RemoveContactFromList(all=True)

        try:
            remove_response: PostContactInfo = contacts_api_instance.remove_contact_from_list(
                sib_list_id, remove_contact
            )
            logger.info("ContactsApi->remove_contact_from_list(%d) returned: %s", sib_list_id, remove_response)

            # While developing, this process takes up to 25 seconds to remove 2 contacts from the list!
            # We must wait until process LIST_USERS_DELETE is completed, otherwise it may remove a contact which was
            # re-added in next process IMPORTUSER
            if remove_response.contacts.process_id:
                _wait_for_process(process_api_instance, remove_response.contacts.process_id)

        except SendinblueApiException as exception:
            if exception.status == 524:
                # Handled first because response is a generic html page, not the expected json body
                logger.exception("Timeout when calling ContactsApi->remove_contact_from_list(%d)", sib_list_id)
                return False
            try:
                message = json.loads(exception.body).get("message")
            except json.JSONDecodeError:
                message = exception.body
            if exception.status == 400 and message == "Contacts already removed from list and/or does not exist":
                logger.info("ContactsApi->remove_contact_from_list(%d): list was already empty", sib_list_id)
            else:
                logger.exception(
                    "Exception when calling ContactsApi->remove_contact_from_list(%d): %s",
                    sib_list_id,
                    exception,
                )
                return False

    # Add contacts API is limited to 150 email addresses:
    # https://developers.sendinblue.com/reference/addcontacttolist-1
    # So use bulk import (up to 8 MB CSV data):
    # https://developers.sendinblue.com/reference/importcontacts-1
    try:
        # Let's put 200k emails addresses per API call, which allows an average email length of 41 characters to ensure
        # that the body is not bigger than 8 MB. Reading statistics, the average address length is between 20 and 25.
        # We are safe :-)
        max_emails_per_import = 200000
        process_ids = []

        def chunk(it, size) -> Iterable:  # type: ignore [no-untyped-def]
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())

        for emails in chunk(user_emails, max_emails_per_import):
            file_body = "EMAIL\n" + "\n".join(emails)
            process_ids.append(_send_import_request(contacts_api_instance, sib_list_id, len(emails), file_body))

        for process_id in process_ids:
            _wait_for_process(process_api_instance, process_id)

    except SendinblueApiException as exception:
        logger.exception("Exception when calling ContactsApi->import_contacts: %s", exception)
        return False

    return True
