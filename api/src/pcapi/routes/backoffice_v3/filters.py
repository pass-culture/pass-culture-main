import datetime
import typing
from urllib.parse import urlparse
from urllib.parse import urlunparse

from flask import Flask
import pytz

from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import subcategories_v2
from pcapi.core.offerers import models as offerers_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.utils import urls


PARIS_TZ = pytz.timezone("Europe/Paris")


def format_state(is_active: bool) -> str:
    if is_active:
        return "Actif"
    return "Suspendu"


def format_role(role: str | None) -> str:
    if not role:
        return "Aucune information"

    match role:
        case users_models.UserRole.ADMIN:
            return "Admin"
        case users_models.UserRole.PRO:
            return "Pro"
        case users_models.UserRole.TEST:
            return "Test"
        case users_models.UserRole.BENEFICIARY:
            return "Pass 18"
        case users_models.UserRole.UNDERAGE_BENEFICIARY:
            return "Pass 15-17"
        case _:
            return "Aucune information"


def format_phone_number(phone_number: str) -> str:
    if not phone_number:
        return ""

    return phone_number


def empty_string_if_null(data: typing.Any | None) -> str:
    if data is None:
        return ""
    return str(data)


def format_date(data: datetime.date | datetime.datetime, strformat: str = "%d/%m/%Y") -> str:
    if not data:
        return ""
    if isinstance(data, datetime.datetime):
        return data.astimezone(PARIS_TZ).strftime(strformat)
    return data.strftime(strformat)


def format_amount(amount: float | None) -> str:
    if amount is None:
        amount = 0.0

    return f"{amount:,.2f} €".replace(",", "\u202f").replace(".", ",")


def format_bool(data: bool | None) -> str:
    if data is None:
        return ""

    if data:
        return "Oui"
    return "Non"


def format_string_list(data: list[str] | None) -> str:
    if data is None:
        return ""
    return ", ".join(data)


def format_reason_label(reason: str) -> str:
    return users_constants.SUSPENSION_REASON_CHOICES.get(users_constants.SuspensionReason(reason), "Raison inconnue")


def format_booking_cancellation_reason(reason: bookings_models.BookingCancellationReasons) -> str:
    match reason:
        case bookings_models.BookingCancellationReasons.OFFERER:
            return "Annulée par l'acteur culturel"
        case bookings_models.BookingCancellationReasons.BENEFICIARY:
            return "Annulée par le bénéficiaire"
        case bookings_models.BookingCancellationReasons.EXPIRED:
            return "Expirée"
        case bookings_models.BookingCancellationReasons.FRAUD:
            return "Fraude"
        case bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE:
            return "Refusée par l'institution"
        case _:
            return ""


def format_booking_status_long(status: bookings_models.BookingStatus) -> str:
    match status:
        case bookings_models.BookingStatus.CONFIRMED:
            return "Réservation confirmée"
        case bookings_models.BookingStatus.USED:
            return "Le jeune a consommé l'offre"
        case bookings_models.BookingStatus.CANCELLED:
            return "L'offre n'a pas eu lieu"
        case bookings_models.BookingStatus.REIMBURSED:
            return "AC remboursé"
        case _:
            return status.value


def format_booking_status(status: bookings_models.BookingStatus) -> str:
    match status:
        case bookings_models.BookingStatus.CONFIRMED:
            return "Confirmée"
        case bookings_models.BookingStatus.USED:
            return "Validée"
        case bookings_models.BookingStatus.CANCELLED:
            return "Annulée"
        case bookings_models.BookingStatus.REIMBURSED:
            return "Remboursée"
        case _:
            return status.value


def format_offer_category(subcategory_id: str) -> str:
    subcategory = subcategories_v2.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if subcategory:
        return subcategory.category.pro_label
    return ""


def format_offerer_tags(offerer_tags: list[offerers_models.OffererTag]) -> str:
    return ", ".join([tag.label for tag in offerer_tags])


def parse_referrer(url: str) -> str:
    """
    Ensure that a relative path is used, which will be understood.
    Referrer can be modified by the client, therefore cannot be trusted.
    """
    try:
        parsed = urlparse(url)
        return urlunparse(("", "", parsed.path, parsed.params, parsed.query, parsed.fragment))
    except Exception:  # pylint: disable=broad-except
        return "/"


def install_template_filters(app: Flask) -> None:
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
    app.jinja_env.filters["format_amount"] = format_amount
    app.jinja_env.filters["format_booking_cancellation_reason"] = format_booking_cancellation_reason
    app.jinja_env.filters["format_booking_status"] = format_booking_status
    app.jinja_env.filters["format_booking_status_long"] = format_booking_status_long
    app.jinja_env.filters["format_bool"] = format_bool
    app.jinja_env.filters["format_string_list"] = format_string_list
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_offer_category"] = format_offer_category
    app.jinja_env.filters["format_offerer_tags"] = format_offerer_tags
    app.jinja_env.filters["format_phone_number"] = format_phone_number
    app.jinja_env.filters["format_role"] = format_role
    app.jinja_env.filters["format_state"] = format_state
    app.jinja_env.filters["format_reason_label"] = format_reason_label
    app.jinja_env.filters["parse_referrer"] = parse_referrer
    app.jinja_env.filters["pc_pro_offer_link"] = urls.build_pc_pro_offer_link
    app.jinja_env.filters["pc_pro_offerer_link"] = urls.build_pc_pro_offerer_link
    app.jinja_env.filters["pc_pro_venue_link"] = urls.build_pc_pro_venue_link
