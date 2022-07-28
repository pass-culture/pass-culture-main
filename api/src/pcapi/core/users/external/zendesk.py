"""
Update user profile attributes in Zendesk to help support team check information quickly.
This module is called when webhook receives a ticket update notification.

Zendesk subscription does not include access to sandbox for testing and staging.
So ZENDESK_API_URL will be empty for non-production platforms, except when working with a free evaluation account which
is limited to 14 days after creation.
"""
from datetime import datetime
import logging
from typing import Iterable
from urllib.parse import quote

from markupsafe import Markup

from pcapi import settings
from pcapi.core.subscription.phone_validation import exceptions as phone_validation_exceptions
from pcapi.core.users import constants as users_constants
from pcapi.core.users import testing
from pcapi.core.users import utils as users_utils
from pcapi.core.users.external import ProAttributes
from pcapi.core.users.external import UserAttributes
from pcapi.core.users.external import get_pro_attributes
from pcapi.core.users.external import get_user_attributes
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import find_user_by_email
from pcapi.utils import phone_number as phone_number_utils
from pcapi.utils import requests


logger = logging.getLogger(__name__)

ZENDESK_TAG_ACTIVE = "actif"
ZENDESK_TAG_DEPARTMENT_CODE_PREFIX = "département_"
ZENDESK_TAG_ELIGIBLE = "éligible"
ZENDESK_TAG_ID_CHECK_COMPLETED = "id_check_terminé"
ZENDESK_TAG_SUSPENDED = "suspendu"


def _get_backoffice_support_beneficiary_user_links(user_id: int) -> list[str]:
    return [
        f"{settings.API_URL}/pc/back-office/support_beneficiary/details/?id={user_id}",
        f"{settings.API_URL}/pc/back-office/beneficiary_users/details/?id={user_id}",
    ]


def _get_backoffice_pro_user_links(email: str) -> list[str]:
    return [
        f"{settings.API_URL}/pc/back-office/pro_users/?search={quote(email)}",
        f"{settings.API_URL}/pc/back-office/userofferer/?flt1_0={quote(email)}",
    ]


def _get_backoffice_venues_link(venues_ids: Iterable[int]) -> str:
    sorted_venues_ids = sorted([str(venue_id) for venue_id in venues_ids])
    return f"{settings.API_URL}/pc/back-office/venue/?flt3_26={'%2C'.join(sorted_venues_ids)}"


def _format_list(raw_list: Iterable[str] | None) -> str | None:
    return ", ".join(raw_list) if raw_list else None


def update_contact_attributes(
    is_new_ticket: bool, ticket_id: int, zendesk_user_id: int, email: str | None, phone_number: str | None
) -> None:

    # First search for user by email (unique in "user" table)
    user: User | None = find_user_by_email(email) if email else None

    # Then search by phone number, which is NOT unique in user database
    # TODO(prouzet) Should we search by phone number in venues?
    if not user and phone_number:
        user = User.query.filter(User.phoneNumber.like(f"%{phone_number[-9:]}")).first()  # type: ignore [attr-defined]

    if user and not email:
        email = user.email

    if user and not user.has_pro_role:
        attributes = get_user_attributes(user)
    elif email:
        # get_pro_attributes also search for email in venues
        attributes = get_pro_attributes(email)
        if not attributes.is_user_email and not attributes.is_booking_email:
            return  # not found
    else:
        return  # not found

    _send_contact_attributes(zendesk_user_id, email, attributes)
    if is_new_ticket:
        _add_internal_note(ticket_id, zendesk_user_id, email, attributes)


def _format_user_attributes(email: str, attributes: UserAttributes) -> dict:
    # https://developer.zendesk.com/api-reference/ticketing/users/users/#phone-number
    try:
        parsed_phone_number = phone_number_utils.parse_phone_number(
            attributes.phone_number,  # type: ignore [arg-type]
            "FR",
        )
        phone_number = phone_number_utils.get_formatted_phone_number(parsed_phone_number)
    except phone_validation_exceptions.InvalidPhoneNumber:
        phone_number = None

    suspended = (
        "Non"
        if attributes.is_active
        else "Oui - {} ({})".format(
            dict(users_constants.SUSPENSION_REASON_CHOICES).get(attributes.suspension_reason, "raison inconnue"),  # type: ignore [call-overload]
            datetime.strftime(attributes.suspension_date, "le %d/%m/%Y à %H:%M")
            if attributes.suspension_date and attributes.suspension_reason
            else "date inconnue",
        )
    )

    tags = attributes.roles.copy()
    tags.append(ZENDESK_TAG_ACTIVE if attributes.is_active else ZENDESK_TAG_SUSPENDED)
    if attributes.has_completed_id_check:
        tags.append(ZENDESK_TAG_ID_CHECK_COMPLETED)
    if attributes.is_eligible:
        tags.append(ZENDESK_TAG_ELIGIBLE)

    return {
        "email": email,
        "phone": phone_number,
        "tags": tags,
        # https://developer.zendesk.com/api-reference/ticketing/users/users/#user-fields
        "user_fields": {
            "backoffice_url": _get_backoffice_support_beneficiary_user_links(attributes.user_id)[0],
            "user_id": attributes.user_id,
            "first_name": attributes.first_name,
            "last_name": attributes.last_name,
            "postal_code": attributes.postal_code,
            "date_of_birth": attributes.date_of_birth.date().isoformat() if attributes.date_of_birth else None,
            "suspended": suspended,
            "email_validated": attributes.is_email_validated,
            "phone_validated": attributes.is_phone_validated,
            "initial_credit": float(attributes.domains_credit.all.initial) if attributes.domains_credit else 0,
            "remaining_credit": float(attributes.domains_credit.all.remaining) if attributes.domains_credit else 0,
        },
    }


def _format_pro_attributes(email: str, attributes: ProAttributes) -> dict:
    tags = [UserRole.PRO.value]
    if attributes.departement_code:
        tags += [ZENDESK_TAG_DEPARTMENT_CODE_PREFIX + code for code in attributes.departement_code]
    return {
        "email": email,
        "tags": tags,
        # https://developer.zendesk.com/api-reference/ticketing/users/users/#user-fields
        "user_fields": {
            "backoffice_url": _get_backoffice_pro_user_links(email)[0]
            if attributes.user_id
            else _get_backoffice_venues_link(attributes.venues_ids),
            "user_id": attributes.user_id,
            "first_name": attributes.first_name,
            "last_name": attributes.last_name,
            "postal_code": _format_list(attributes.postal_code),
            "offerer_name": _format_list(attributes.offerers_names),
            "venue_name": _format_list(attributes.venues_names),
            "dms_application": "Approuvé"
            if attributes.dms_application_approved
            else "Déposé"
            if attributes.dms_application_submitted
            else "Aucun",
        },
    }


def format_contact_attributes(email: str, attributes: UserAttributes | ProAttributes) -> dict:
    if isinstance(attributes, ProAttributes):
        return _format_pro_attributes(email, attributes)
    return _format_user_attributes(email, attributes)


def _send_contact_attributes(zendesk_user_id: int, email: str, attributes: UserAttributes | ProAttributes) -> bool:
    """
    Update user with custom attributes
    https://developer.zendesk.com/api-reference/ticketing/users/users/#update-user
    """
    data = {"user": format_contact_attributes(email, attributes)}

    return _put_to_zendesk(zendesk_user_id, f"/users/{zendesk_user_id}", data)


def _add_internal_note(
    ticket_id: int, zendesk_user_id: int, email: str, attributes: UserAttributes | ProAttributes
) -> bool:
    """
    Post an internal note so that support people can click on hyperlinks (not possible with custom attributes)
    https://developer.zendesk.com/api-reference/ticketing/tickets/ticket_comments/
    """
    html_body = Markup("<i>Note automatique générée par le backend pass Culture ({})</i><br/>").format(settings.ENV)

    name = (
        f"{attributes.first_name} {attributes.last_name}"
        if attributes.first_name and attributes.last_name
        else f"id {attributes.user_id}"
    )

    if isinstance(attributes, ProAttributes):
        if attributes.user_id:
            html_body += Markup("Utilisateur pro identifié : <b>{}</b><br/>, {}").format(name, email)
            for bo_link in _get_backoffice_pro_user_links(email):
                html_body += Markup('<a href="{}" target="_blank">{}</a><br/>').format(bo_link, bo_link)
        if attributes.venues_ids:
            venue_count = len(set(attributes.venues_ids))
            html_body += f"{venue_count} lieux identifiés :" if venue_count > 1 else "1 lieu identifié :"
            bo_link = _get_backoffice_venues_link(attributes.venues_ids)
            html_body += Markup('<br/><a href="{}" target="_blank">{}</a><br/>').format(bo_link, bo_link)
    else:
        html_body += Markup("Utilisateur identifié : <b>{}</b>, {}").format(name, email)
        if attributes.date_of_birth:
            html_body += f", {users_utils.get_age_from_birth_date(attributes.date_of_birth)} ans"
        if attributes.is_beneficiary and attributes.domains_credit:
            html_body += Markup("<br/>Bénéficiaire, crédit restant : {remaining:.2f} € sur {initial:.2f} €").format(
                remaining=float(attributes.domains_credit.all.remaining) if attributes.domains_credit else 0,
                initial=float(attributes.domains_credit.all.initial) if attributes.domains_credit else 0,
            )
        for bo_link in _get_backoffice_support_beneficiary_user_links(attributes.user_id):
            html_body += Markup('<br/><a href="{}" target="_blank">{}</a>').format(bo_link, bo_link)

    data = {
        "ticket": {
            "comment": {
                "html_body": html_body,
                "public": False,
                "type": "Comment",
            }
        }
    }

    return _put_to_zendesk(zendesk_user_id, f"/tickets/{ticket_id}.json", data)


def _put_to_zendesk(zendesk_user_id: int, route: str, data: dict) -> bool:
    if settings.IS_RUNNING_TESTS:
        testing.zendesk_requests.append({"zendesk_user_id": zendesk_user_id, "data": data})
        return True

    if settings.IS_DEV or not settings.ZENDESK_API_URL:
        logger.info("A request to Zendesk API would be sent for user %s with data %s", zendesk_user_id, data)
        return True

    try:
        response = requests.put(
            f"{settings.ZENDESK_API_URL.rstrip('/')}{route}",
            auth=(f"{settings.ZENDESK_API_EMAIL}/token", settings.ZENDESK_API_TOKEN),
            json=data,
        )
        response.raise_for_status()
        return True
    except Exception as exception:  # pylint: disable=broad-except
        logger.exception(
            "Exception when calling Zendesk API: %e",
            exception,
            extra={"zendesk_user_id": zendesk_user_id, "route": route, "data": data},
        )
        return False
