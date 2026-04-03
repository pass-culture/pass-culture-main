import enum
import logging
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from itertools import islice
from typing import Any
from typing import Callable
from typing import Iterable

import brevo
from brevo.core import ApiError as BrevoApiError

from pcapi import settings
from pcapi.core import mails as mails_api
from pcapi.core.cultural_survey import models as cultural_survey_models
from pcapi.core.external.attributes import models as attributes_models
from pcapi.core.mails import serialization
from pcapi.core.mails import tasks
from pcapi.core.users import models as users_models


logger = logging.getLogger(__name__)


@dataclass
class BrevoUserUpdateData:
    email: str
    attributes: dict


class BrevoAttributes(Enum):
    ACHIEVEMENTS = "ACHIEVEMENTS"
    BONIFICATION_STATUS = "BONIFICATION_STATUS"
    BOOKED_OFFER_CATEGORIES = "BOOKED_OFFER_CATEGORIES"
    BOOKED_OFFER_CATEGORIES_COUNT = "BOOKED_OFFER_CATEGORIES_COUNT"
    BOOKED_OFFER_SUBCATEGORIES = "BOOKED_OFFER_SUBCATEGORIES"
    BOOKING_COUNT = "BOOKING_COUNT"
    BOOKING_VENUES_COUNT = "BOOKING_VENUES_COUNT"
    CREDIT = "CREDIT"
    DATE_CREATED = "DATE_CREATED"
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    DEPARTMENT_CODE = "DEPARTMENT_CODE"
    DEPOSITS_COUNT = "DEPOSITS_COUNT"
    DEPOSIT_ACTIVATION_DATE = "DEPOSIT_ACTIVATION_DATE"
    DEPOSIT_EXPIRATION_DATE = "DEPOSIT_EXPIRATION_DATE"
    DMS_APPLICATION_APPROVED = "DMS_APPLICATION_APPROVED"
    DMS_APPLICATION_SUBMITTED = "DMS_APPLICATION_SUBMITTED"
    ELIGIBILITY = "ELIGIBILITY"
    FIRSTNAME = "FIRSTNAME"
    HAS_BANNER_URL = "HAS_BANNER_URL"
    HAS_BOOKINGS = "HAS_BOOKINGS"
    HAS_COLLECTIVE_OFFERS = "HAS_COLLECTIVE_OFFERS"
    HAS_COMPLETED_ID_CHECK = "HAS_COMPLETED_ID_CHECK"
    HAS_INDIVIDUAL_OFFERS = "HAS_INDIVIDUAL_OFFERS"
    HAS_OFFERS = "HAS_OFFERS"
    INITIAL_CREDIT = "INITIAL_CREDIT"
    IS_ACTIVE_PRO = "IS_ACTIVE_PRO"
    IS_BENEFICIARY = "IS_BENEFICIARY"
    IS_BENEFICIARY_18 = "IS_BENEFICIARY_18"
    IS_BOOKING_EMAIL = "IS_BOOKING_EMAIL"
    IS_CURRENT_BENEFICIARY = "IS_CURRENT_BENEFICIARY"
    IS_FORMER_BENEFICIARY = "IS_FORMER_BENEFICIARY"
    IS_ELIGIBLE = "IS_ELIGIBLE"
    IS_EMAIL_VALIDATED = "IS_EMAIL_VALIDATED"
    IS_PERMANENT = "IS_PERMANENT"
    IS_OPEN_TO_PUBLIC = "IS_OPEN_TO_PUBLIC"
    IS_PRO = "IS_PRO"
    IS_UNDERAGE_BENEFICIARY = "IS_UNDERAGE_BENEFICIARY"
    IS_USER_EMAIL = "IS_USER_EMAIL"
    IS_VIRTUAL = "IS_VIRTUAL"
    LAST_BOOKING_DATE = "LAST_BOOKING_DATE"
    LAST_FAVORITE_CREATION_DATE = "LAST_FAVORITE_CREATION_DATE"
    LAST_RECREDIT_TYPE = "LAST_RECREDIT_TYPE"
    LAST_VISIT_DATE = "LAST_VISIT_DATE"
    LASTNAME = "LASTNAME"
    MARKETING_EMAIL_SUBSCRIPTION = "MARKETING_EMAIL_SUBSCRIPTION"
    MOST_BOOKED_OFFER_SUBCATEGORY = "MOST_BOOKED_OFFER_SUBCATEGORY"
    MOST_BOOKED_MOVIE_GENRE = "MOST_BOOKED_MOVIE_GENRE"
    MOST_BOOKED_MUSIC_TYPE = "MOST_BOOKED_MUSIC_TYPE"
    MOST_FAVORITE_OFFER_SUBCATEGORIES = "MOST_FAVORITE_OFFER_SUBCATEGORIES"
    OFFERER_NAME = "OFFERER_NAME"
    OFFERER_TAG = "OFFERER_TAG"
    PERMANENT_THEME_PREFERENCE = "PERMANENT_THEME_PREFERENCE"
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
    EAC_MEG = "EAC_MEG"
    IS_EAC_MEG = "IS_EAC_MEG"  # for pro attributes

    @classmethod
    def list(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class BrevoOptionalAttributes(Enum):
    # Not in BrevoAttributes because of build_file_body which uses full list()
    # We don't want one-shot attributes in bulk import
    INTENDED_CATEGORIES = "INTENDED_CATEGORIES"


def _get_brevo_client(use_pro_subaccount: bool) -> brevo.Brevo:
    api_key = settings.SENDINBLUE_PRO_API_KEY if use_pro_subaccount else settings.SENDINBLUE_API_KEY
    return brevo.Brevo(api_key=api_key, timeout=settings.BREVO_REQUEST_TIMEOUT)


def update_contact_email(user: users_models.User, old_email: str, new_email: str, asynchronous: bool = True) -> None:
    if user.has_any_pro_role:
        contact_list_ids = None
    else:
        contact_list_ids = [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]

    contact_request = serialization.UpdateBrevoContactRequest(
        email=old_email,
        use_pro_subaccount=user.has_any_pro_role,
        attributes={"EMAIL": new_email},
        contact_list_ids=contact_list_ids,
        emailBlacklisted=(not user.get_notification_subscriptions().marketing_email),
    )

    if asynchronous:
        tasks.update_contact_attributes_task.delay(contact_request.model_dump())
    else:
        tasks.update_contact_attributes_task(contact_request.model_dump())


def update_contact_attributes(
    user_email: str,
    attributes: attributes_models.UserAttributes | attributes_models.ProAttributes,
    cultural_survey_answers: dict[str, list[str]] | None = None,
    asynchronous: bool = True,
) -> None:
    if attributes.is_pro:
        assert isinstance(attributes, attributes_models.ProAttributes)  # helps mypy
        formatted_attributes = format_pro_attributes(attributes)
        contact_list_ids = None
    else:
        formatted_attributes = format_user_attributes(attributes)
        if cultural_survey_answers:
            formatted_attributes.update(format_cultural_survey_answers(cultural_survey_answers))
        contact_list_ids = [settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID]

    contact_request = serialization.UpdateBrevoContactRequest(
        email=user_email,
        use_pro_subaccount=attributes.is_pro,
        attributes=formatted_attributes,
        contact_list_ids=contact_list_ids,
        emailBlacklisted=(not attributes.marketing_email_subscription),  # attribute may be None
    )

    if asynchronous:
        tasks.update_contact_attributes_task.delay(contact_request.model_dump())
    else:
        make_update_request(contact_request)


def format_list(raw_list: Iterable[str] | None) -> str:
    if not raw_list:
        return ""
    return ",".join(raw_list)


def format_list_or_str(raw_value: str | Iterable[str]) -> str:
    if isinstance(raw_value, str):
        return raw_value
    return format_list(raw_value)


def format_enum(enum_value: enum.Enum | str) -> str:
    if isinstance(enum_value, str):
        return enum_value
    return enum_value.value


def _get_attr(
    attributes: attributes_models.UserAttributes | attributes_models.ProAttributes,
    name: str,
    func: Callable[[Any], Any] | None = None,
) -> Any:
    value = getattr(attributes, name, None)
    if value is not None and func is not None:
        value = func(value)
    return value


def format_user_attributes(attributes: attributes_models.UserAttributes | attributes_models.ProAttributes) -> dict:
    result = {
        BrevoAttributes.ACHIEVEMENTS.value: _get_attr(attributes, "achievements", format_list),
        BrevoAttributes.BONIFICATION_STATUS.value: _get_attr(attributes, "bonification_status", format_enum),
        BrevoAttributes.BOOKED_OFFER_CATEGORIES.value: _get_attr(attributes, "booking_categories", format_list),
        BrevoAttributes.BOOKED_OFFER_CATEGORIES_COUNT.value: _get_attr(attributes, "booking_categories", len),
        BrevoAttributes.BOOKED_OFFER_SUBCATEGORIES.value: _get_attr(attributes, "booking_subcategories", format_list),
        BrevoAttributes.BOOKING_COUNT.value: _get_attr(attributes, "booking_count"),
        BrevoAttributes.BOOKING_VENUES_COUNT.value: _get_attr(attributes, "booking_venues_count"),
        BrevoAttributes.CREDIT.value: _get_attr(attributes, "domains_credit", lambda v: v.all.remaining),
        BrevoAttributes.DATE_CREATED.value: _get_attr(attributes, "date_created"),
        BrevoAttributes.DATE_OF_BIRTH.value: _get_attr(attributes, "date_of_birth"),
        BrevoAttributes.DEPARTMENT_CODE.value: _get_attr(attributes, "departement_code", format_list_or_str),
        BrevoAttributes.DEPOSITS_COUNT.value: _get_attr(attributes, "deposits_count"),
        BrevoAttributes.DEPOSIT_ACTIVATION_DATE.value: _get_attr(attributes, "deposit_activation_date"),
        BrevoAttributes.DEPOSIT_EXPIRATION_DATE.value: _get_attr(attributes, "deposit_expiration_date"),
        BrevoAttributes.DMS_APPLICATION_APPROVED.value: _get_attr(attributes, "dms_application_approved"),
        BrevoAttributes.DMS_APPLICATION_SUBMITTED.value: _get_attr(attributes, "dms_application_submitted"),
        BrevoAttributes.ELIGIBILITY.value: _get_attr(attributes, "eligibility", format_enum),
        BrevoAttributes.FIRSTNAME.value: _get_attr(attributes, "first_name"),
        BrevoAttributes.HAS_BANNER_URL.value: _get_attr(attributes, "has_banner_url"),
        BrevoAttributes.HAS_BOOKINGS.value: _get_attr(attributes, "has_bookings"),
        BrevoAttributes.HAS_COLLECTIVE_OFFERS.value: _get_attr(attributes, "has_collective_offers"),
        BrevoAttributes.HAS_COMPLETED_ID_CHECK.value: _get_attr(attributes, "has_completed_id_check"),
        BrevoAttributes.HAS_INDIVIDUAL_OFFERS.value: _get_attr(attributes, "has_individual_offers"),
        BrevoAttributes.HAS_OFFERS.value: _get_attr(attributes, "has_offers"),
        BrevoAttributes.INITIAL_CREDIT.value: _get_attr(attributes, "domains_credit", lambda v: v.all.initial),
        BrevoAttributes.IS_ACTIVE_PRO.value: _get_attr(attributes, "is_active_pro"),
        BrevoAttributes.IS_BENEFICIARY.value: _get_attr(attributes, "is_beneficiary"),
        BrevoAttributes.IS_BENEFICIARY_18.value: _get_attr(
            attributes, "roles", lambda v: users_models.UserRole.BENEFICIARY.value in v
        ),
        BrevoAttributes.IS_BOOKING_EMAIL.value: _get_attr(attributes, "is_booking_email"),
        BrevoAttributes.IS_CURRENT_BENEFICIARY.value: _get_attr(attributes, "is_current_beneficiary"),
        BrevoAttributes.IS_FORMER_BENEFICIARY.value: _get_attr(attributes, "is_former_beneficiary"),
        BrevoAttributes.IS_ELIGIBLE.value: _get_attr(attributes, "is_eligible"),
        BrevoAttributes.IS_EMAIL_VALIDATED.value: _get_attr(attributes, "is_email_validated"),
        BrevoAttributes.IS_PERMANENT.value: _get_attr(attributes, "isPermanent"),
        BrevoAttributes.IS_OPEN_TO_PUBLIC.value: _get_attr(attributes, "isOpenToPublic"),
        BrevoAttributes.IS_PRO.value: _get_attr(attributes, "is_pro"),
        BrevoAttributes.IS_UNDERAGE_BENEFICIARY.value: _get_attr(
            attributes, "roles", lambda v: users_models.UserRole.UNDERAGE_BENEFICIARY.value in v
        ),
        BrevoAttributes.IS_USER_EMAIL.value: _get_attr(attributes, "is_user_email"),
        BrevoAttributes.IS_VIRTUAL.value: _get_attr(attributes, "isVirtual"),
        BrevoAttributes.LAST_BOOKING_DATE.value: _get_attr(attributes, "last_booking_date"),
        BrevoAttributes.LAST_FAVORITE_CREATION_DATE.value: _get_attr(attributes, "last_favorite_creation_date"),
        BrevoAttributes.LAST_RECREDIT_TYPE.value: _get_attr(attributes, "last_recredit_type", format_enum),
        BrevoAttributes.LAST_VISIT_DATE.value: _get_attr(attributes, "last_visit_date"),
        BrevoAttributes.LASTNAME.value: _get_attr(attributes, "last_name"),
        BrevoAttributes.MARKETING_EMAIL_SUBSCRIPTION.value: _get_attr(attributes, "marketing_email_subscription"),
        BrevoAttributes.MOST_BOOKED_OFFER_SUBCATEGORY.value: _get_attr(attributes, "most_booked_subcategory"),
        BrevoAttributes.MOST_BOOKED_MOVIE_GENRE.value: _get_attr(attributes, "most_booked_movie_genre"),
        BrevoAttributes.MOST_BOOKED_MUSIC_TYPE.value: _get_attr(attributes, "most_booked_music_type"),
        BrevoAttributes.MOST_FAVORITE_OFFER_SUBCATEGORIES.value: _get_attr(
            attributes, "most_favorite_offer_subcategories", format_list
        ),
        BrevoAttributes.OFFERER_NAME.value: _get_attr(attributes, "offerers_names", format_list),
        BrevoAttributes.OFFERER_TAG.value: _get_attr(attributes, "offerers_tags", format_list),
        BrevoAttributes.PERMANENT_THEME_PREFERENCE.value: _get_attr(attributes, "subscribed_themes", format_list) or "",
        BrevoAttributes.POSTAL_CODE.value: _get_attr(attributes, "postal_code", format_list_or_str),
        BrevoAttributes.PRODUCT_BRUT_X_USE_DATE.value: _get_attr(
            attributes, "products_use_date", lambda v: v.get("product_brut_x_use")
        ),
        BrevoAttributes.USER_ID.value: _get_attr(attributes, "user_id"),
        BrevoAttributes.USER_IS_ATTACHED.value: _get_attr(attributes, "user_is_attached"),
        BrevoAttributes.USER_IS_CREATOR.value: _get_attr(attributes, "user_is_creator"),
        BrevoAttributes.VENUE_COUNT.value: _get_attr(attributes, "venues_ids", len),
        BrevoAttributes.VENUE_LABEL.value: _get_attr(attributes, "venues_labels", format_list),
        BrevoAttributes.VENUE_NAME.value: _get_attr(attributes, "venues_names", format_list),
        BrevoAttributes.VENUE_TYPE.value: _get_attr(attributes, "venues_types", format_list),
        BrevoAttributes.IS_EAC.value: _get_attr(attributes, "is_eac"),
        BrevoAttributes.EAC_MEG.value: _get_attr(attributes, "is_eac_meg"),
    }

    return result


def format_pro_attributes(attributes: attributes_models.ProAttributes) -> dict:
    return {
        BrevoAttributes.DMS_APPLICATION_APPROVED.value: _get_attr(attributes, "dms_application_approved"),
        BrevoAttributes.DMS_APPLICATION_SUBMITTED.value: _get_attr(attributes, "dms_application_submitted"),
        BrevoAttributes.FIRSTNAME.value: _get_attr(attributes, "first_name"),
        BrevoAttributes.HAS_BANNER_URL.value: _get_attr(attributes, "has_banner_url"),
        BrevoAttributes.HAS_BOOKINGS.value: _get_attr(attributes, "has_bookings"),
        BrevoAttributes.HAS_COLLECTIVE_OFFERS.value: _get_attr(attributes, "has_collective_offers"),
        BrevoAttributes.HAS_INDIVIDUAL_OFFERS.value: _get_attr(attributes, "has_individual_offers"),
        BrevoAttributes.HAS_OFFERS.value: _get_attr(attributes, "has_offers"),
        BrevoAttributes.IS_ACTIVE_PRO.value: _get_attr(attributes, "is_active_pro"),
        BrevoAttributes.IS_BOOKING_EMAIL.value: _get_attr(attributes, "is_booking_email"),
        BrevoAttributes.IS_EAC.value: _get_attr(attributes, "is_eac"),
        BrevoAttributes.IS_EAC_MEG.value: _get_attr(attributes, "is_eac_meg"),
        BrevoAttributes.IS_PERMANENT.value: _get_attr(attributes, "isPermanent"),
        BrevoAttributes.IS_OPEN_TO_PUBLIC.value: _get_attr(attributes, "isOpenToPublic"),
        BrevoAttributes.IS_PRO.value: _get_attr(attributes, "is_pro"),
        BrevoAttributes.IS_USER_EMAIL.value: _get_attr(attributes, "is_user_email"),
        BrevoAttributes.IS_VIRTUAL.value: _get_attr(attributes, "isVirtual"),
        BrevoAttributes.LASTNAME.value: _get_attr(attributes, "last_name"),
        BrevoAttributes.MARKETING_EMAIL_SUBSCRIPTION.value: _get_attr(attributes, "marketing_email_subscription"),
        BrevoAttributes.OFFERER_NAME.value: _get_attr(attributes, "offerers_names", format_list),
        BrevoAttributes.OFFERER_TAG.value: _get_attr(attributes, "offerers_tags", format_list),
        BrevoAttributes.USER_ID.value: _get_attr(attributes, "user_id"),
        BrevoAttributes.USER_IS_ATTACHED.value: _get_attr(attributes, "user_is_attached"),
        BrevoAttributes.USER_IS_CREATOR.value: _get_attr(attributes, "user_is_creator"),
        BrevoAttributes.VENUE_COUNT.value: _get_attr(attributes, "venues_ids", len),
        BrevoAttributes.VENUE_LABEL.value: _get_attr(attributes, "venues_labels", format_list),
        BrevoAttributes.VENUE_NAME.value: _get_attr(attributes, "venues_names", format_list),
        BrevoAttributes.VENUE_TYPE.value: _get_attr(attributes, "venues_types", format_list),
    }


def format_cultural_survey_answers(cultural_survey_answers: dict[str, list[str]]) -> dict:
    return {
        BrevoOptionalAttributes.INTENDED_CATEGORIES.value: format_list(
            cultural_survey_answers.get(cultural_survey_models.CulturalSurveyQuestionEnum.PROJECTIONS.value)
        )
    }


def make_update_request(payload: serialization.UpdateBrevoContactRequest) -> None:
    mails_api.create_contact(payload)


def send_import_contacts_request(
    client: brevo.Brevo, file_body: str, list_ids: list[int] | None, email_blacklist: bool = False
) -> None:
    try:
        client.contacts.import_contacts(
            email_blacklist=email_blacklist,
            file_body=file_body,
            list_ids=list_ids,
            update_existing_contacts=True,
        )
    except BrevoApiError as e:
        logger.exception("Exception when calling Brevo import_contacts: %s", e)


def format_file_value(value: str | bool | int | datetime | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)


def build_file_body(users_data: list[BrevoUserUpdateData]) -> str:
    """Generates a csv-like string for bulk import, based on BrevoAttributes
       e.g.: "EMAIL;FIRSTNAME;SMS\n#john@example.com;John;Doe;31234567923"

    Args:
        users_data (list[BrevoUserUpdateData]): users data

    Returns:
        str: corresponding csv string
    """
    file_body = ";".join(sorted(BrevoAttributes.list())) + ";EMAIL"
    for user in users_data:
        file_body += "\n"
        file_body += ";".join([format_file_value(value) for _, value in sorted(user.attributes.items())])
        file_body += f";{user.email}"

    return file_body


def import_contacts_in_brevo(brevo_users_data: list[BrevoUserUpdateData], email_blacklist: bool = False) -> None:
    # Split users in Brevo lists
    pro_users = [user_data for user_data in brevo_users_data if user_data.attributes[BrevoAttributes.IS_PRO.value]]
    young_users = [
        user_data for user_data in brevo_users_data if not user_data.attributes[BrevoAttributes.IS_PRO.value]
    ]

    # send pro users request
    # FIXME (prouzet, 2025-03-14): import_contacts_in_brevo is not called when refreshing pro users
    # This part causes an HTTP 400 error: {"code":"missing_parameter","message":"Missing listIds or newList"}
    # List is mandatory when calling import_contacts endpoint.
    if pro_users:
        client = _get_brevo_client(use_pro_subaccount=True)
        pro_users_file_body = build_file_body(pro_users)
        send_import_contacts_request(
            client,
            file_body=pro_users_file_body,
            list_ids=None,
            email_blacklist=email_blacklist,
        )
    # send young users request
    if young_users:
        client = _get_brevo_client(use_pro_subaccount=False)
        young_users_file_body = build_file_body(young_users)
        send_import_contacts_request(
            client,
            file_body=young_users_file_body,
            list_ids=[settings.SENDINBLUE_YOUNG_CONTACT_LIST_ID],
            email_blacklist=email_blacklist,
        )


def _send_import_request(client: brevo.Brevo, brevo_list_id: int, iteration: int, count: int, file_body: str) -> int:
    import_contacts_response = client.contacts.import_contacts(
        file_body=file_body,
        list_ids=[brevo_list_id],
        notify_url=urllib.parse.urljoin(
            settings.API_URL,
            f"/webhooks/sendinblue/importcontacts/{brevo_list_id}/{iteration}",
        ),
    )
    logger.info(
        "Brevo import_contacts returned",
        extra={
            "list_id": brevo_list_id,
            "iteration": iteration,
            "email_count": count,
            "request_body_size": len(file_body),
            "process_id": import_contacts_response.process_id,
        },
    )

    return import_contacts_response.process_id


def add_contacts_to_list(
    user_emails: Iterable[str], brevo_list_id: int, use_pro_subaccount: bool | None = False
) -> bool:
    """
    Fills in a list of contacts using Brevo API.
    This function is intended to be used for automation and returns synchronously (waits for completion).

    Webhook is called when the process is finished on Brevo side: see brevo_notify_importcontacts()

    Args:
        user_emails (Iterable[str]): list or generator of matching user email addresses
        brevo_list_id (int): Brevo list identifier

    Returns:
        bool: True when successful, False otherwise
    """
    client = _get_brevo_client(bool(use_pro_subaccount))

    iteration = 1

    # Add contacts API is limited to 150 email addresses:
    # https://developers.sendinblue.com/reference/addcontacttolist-1
    # So use bulk import (up to 8 MB CSV data):
    # https://developers.sendinblue.com/reference/importcontacts-1
    try:
        # Let's put 200k emails addresses per API call, which allows an average email length of 41 characters to ensure
        # that the body is not bigger than 8 MB. Reading statistics, the average address length is between 20 and 25.
        # We are safe :-)
        max_emails_per_import = 200000

        def chunk(it: Iterable, size: int) -> Iterable:
            it = iter(it)
            return iter(lambda: tuple(islice(it, size)), ())

        for emails in chunk(user_emails, max_emails_per_import):
            file_body = "EMAIL\n" + "\n".join(emails)
            _send_import_request(client, brevo_list_id, iteration, len(emails), file_body)
            iteration += 1

        # Don't wait for processes completed, it would take too much time in the cron process

    except BrevoApiError as exception:
        logger.exception(
            "Exception when calling Brevo import_contacts: %s",
            exception,
            extra={"list_id": brevo_list_id, "iteration": iteration, "use_pro_subaccount": use_pro_subaccount},
        )
        return False

    return True
