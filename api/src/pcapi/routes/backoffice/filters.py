import datetime
import decimal
import html
import logging
import random
import re
import typing
from urllib.parse import urlparse
from urllib.parse import urlunparse

import psycopg2.extras
import pytz
from flask import Flask
from flask import url_for
from markupsafe import Markup
from markupsafe import escape

import pcapi.core.categories.genres.music
from pcapi import settings
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import pro_categories
from pcapi.core.categories.genres import show
from pcapi.core.categories.models import EacFormat
from pcapi.core.categories.subcategories import ALL_SUBCATEGORIES_DICT
from pcapi.core.chronicles import api as chronicles_api
from pcapi.core.chronicles import models as chronicles_models
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.utils import format_collective_offer_displayed_status
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.geography import models as geography_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.operations import models as operations_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription import schemas as subscription_schemas
from pcapi.core.subscription.ubble import api as ubble_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.routes.backoffice.accounts import serialization as serialization_accounts
from pcapi.utils import date as date_utils
from pcapi.utils import urls
from pcapi.utils.csr import Csr
from pcapi.utils.csr import get_csr
from pcapi.utils.date import METROPOLE_TIMEZONE


logger = logging.getLogger(__name__)

PARIS_TZ = pytz.timezone(METROPOLE_TIMEZONE)

ACTION_TYPE_TO_STRING = {
    history_models.ActionType.COMMENT: "Commentaire interne",
    # Update:
    history_models.ActionType.INFO_MODIFIED: "Modification des informations",
    # Validation process for offerers:
    history_models.ActionType.OFFERER_NEW: "Nouvelle entité juridique",
    history_models.ActionType.OFFERER_PENDING: "Entité juridique mise en attente",
    history_models.ActionType.OFFERER_VALIDATED: "Entité juridique validée",
    history_models.ActionType.OFFERER_REJECTED: "Entité juridique rejetée",
    history_models.ActionType.OFFERER_CLOSED: "Entité juridique fermée",
    history_models.ActionType.OFFERER_SUSPENDED: "Entité juridique désactivée",
    history_models.ActionType.OFFERER_UNSUSPENDED: "Entité juridique réactivée",
    history_models.ActionType.OFFERER_ATTESTATION_CHECKED: "Attestation consultée",
    # Validation process for user-offerer relationships:
    history_models.ActionType.USER_OFFERER_NEW: "Nouveau rattachement",
    history_models.ActionType.USER_OFFERER_PENDING: "Rattachement mis en attente",
    history_models.ActionType.USER_OFFERER_VALIDATED: "Rattachement validé",
    history_models.ActionType.USER_OFFERER_REJECTED: "Rattachement rejeté",
    history_models.ActionType.USER_OFFERER_DELETED: "Rattachement supprimé, sans mail envoyé",
    # User account status changes:
    history_models.ActionType.USER_CREATED: "Création du compte",
    history_models.ActionType.USER_SUSPENDED: "Compte suspendu",
    history_models.ActionType.USER_UNSUSPENDED: "Compte réactivé",
    history_models.ActionType.USER_PHONE_VALIDATED: "Validation manuelle du numéro de téléphone",
    history_models.ActionType.USER_EMAIL_VALIDATED: "Validation manuelle de l'email",
    history_models.ActionType.USER_ACCOUNT_UPDATE_INSTRUCTED: "Instruction d'une demande de modifications",
    history_models.ActionType.USER_EXTRACT_DATA: "Génération d'un extrait des données du compte",
    history_models.ActionType.CONNECT_AS_USER: "Connexion d'un admin",
    history_models.ActionType.USER_PASSWORD_INVALIDATED: "Invalidation du mot de passe de l'utilisateur",
    # Fraud and compliance actions:
    history_models.ActionType.BLACKLIST_DOMAIN_NAME: "Blacklist d'un nom de domaine",
    history_models.ActionType.REMOVE_BLACKLISTED_DOMAIN_NAME: "Suppression d'un nom de domaine banni",
    history_models.ActionType.FRAUD_INFO_MODIFIED: "Fraude et Conformité",  # protected information
    # Finance incident events
    history_models.ActionType.FINANCE_INCIDENT_CREATED: "Création de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_CANCELLED: "Annulation de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_VALIDATED: "Validation de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT: "Compte re-crédité suite à un incident",
    history_models.ActionType.FINANCE_INCIDENT_WAIT_FOR_PAYMENT: "Attente de la prochaine échéance de remboursement",
    history_models.ActionType.FINANCE_INCIDENT_GENERATE_DEBIT_NOTE: "Une note de débit va être générée",
    history_models.ActionType.FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE: "Choix note de débit",
    # Actions related to a venue:
    history_models.ActionType.VENUE_CREATED: "Partenaire culturel créé",
    history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED: "Partenaire culturel dissocié d'un compte bancaire",
    history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED: "Partenaire culturel associé à un compte bancaire",
    history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED: "Lien avec le partenaire technique modifié",
    history_models.ActionType.LINK_VENUE_PROVIDER_DELETED: "Suppression du lien avec le partenaire technique",
    history_models.ActionType.SYNC_VENUE_TO_PROVIDER: "Synchronisation du partenaire culturel avec un partenaire technique",
    history_models.ActionType.VENUE_REGULARIZATION: "Régularisation des partenaires culturels",
    history_models.ActionType.VENUE_SOFT_DELETED: "Suppression réversible",
    # Actions related to an offerer and/or a venue:
    history_models.ActionType.NON_PAYMENT_NOTICE_CREATED: "Saisie d'un avis d'impayé",
    # Permissions role changes:
    history_models.ActionType.ROLE_PERMISSIONS_CHANGED: "Modification des permissions du rôle",
    # RGPD scripts
    history_models.ActionType.USER_ANONYMIZED: "Le compte a été anonymisé conformément au RGPD",
    # Offer validation rule changes:
    history_models.ActionType.RULE_CREATED: "Création d'une règle de conformité",
    history_models.ActionType.RULE_DELETED: "Suppression d'une règle de conformité",
    history_models.ActionType.RULE_MODIFIED: "Modification d'une règle de conformité",
    # Pivot changes
    history_models.ActionType.PIVOT_DELETED: "Suppression d'un pivot",
    history_models.ActionType.PIVOT_CREATED: "Création d'un pivot",
    # Chronicles
    history_models.ActionType.CHRONICLE_PUBLISHED: "Publication d'une chronique",
    history_models.ActionType.CHRONICLE_UNPUBLISHED: "Dépublication d'une chronique",
    # User profile refresh campaign
    history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED: "Création de campagne de mise à jour de données",
    history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED: "Modification de campagne de mise à jour de données",
}


def format_action_type(action_type: history_models.ActionType | str) -> str:
    if isinstance(action_type, str):
        return action_type
    try:
        return ACTION_TYPE_TO_STRING[action_type]
    except KeyError:
        logger.error("Missing action type in ACTION_TYPE_TO_STRING: %s", action_type.name)
        return action_type.name


def format_state(is_active: bool) -> str:
    if is_active:
        return "Actif"
    return "Suspendu"


def _get_last_deposit(deposits: list[finance_models.Deposit] | None) -> finance_models.Deposit | None:
    if not deposits:
        return None
    sorted_deposits = sorted(
        deposits,
        key=lambda d: d.expirationDate.timestamp() if d.expirationDate else 2**63,
        reverse=True,
    )
    return sorted_deposits[0]


def format_role(role: str | None, deposits: list[finance_models.Deposit] | None = None) -> str:
    if not role:
        return "Aucune information"

    match role:
        case users_models.UserRole.ADMIN:
            return "Admin"
        case users_models.UserRole.PRO | users_models.UserRole.NON_ATTACHED_PRO:
            return "Pro"
        case users_models.UserRole.TEST:
            return "Test"
        case users_models.UserRole.BENEFICIARY:
            last_deposit = _get_last_deposit(deposits)
            if last_deposit and last_deposit.type == finance_models.DepositType.GRANT_17_18:
                text = "Pass 18"
            else:
                text = "Ancien Pass 18"
            if not last_deposit or (
                last_deposit.expirationDate and last_deposit.expirationDate <= date_utils.get_naive_utc_now()
            ):
                text += " expiré"
            return text
        case users_models.UserRole.UNDERAGE_BENEFICIARY:
            last_deposit = _get_last_deposit(deposits)
            if last_deposit and last_deposit.type == finance_models.DepositType.GRANT_17_18:
                text = "Pass 17"
            else:
                text = "Ancien Pass 15-17"
            if not last_deposit or (
                last_deposit.expirationDate and last_deposit.expirationDate <= date_utils.get_naive_utc_now()
            ):
                text += " expiré"
            return text
        case _:
            return "Aucune information"


def format_user_profile_refresh_campaign_action_type(action_type: history_models.ActionType) -> str:
    match action_type:
        case history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED:
            return "Création"
        case history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED:
            return "Mise à jour"
        case _:
            return action_type.value


def format_deposit_used(booking: bookings_models.Booking) -> str:
    if booking.usedRecreditType:
        if booking.usedRecreditType == bookings_models.BookingRecreditType.RECREDIT_17:
            return format_badge("Pass 17", "secondary")
        if booking.usedRecreditType == bookings_models.BookingRecreditType.RECREDIT_18:
            return format_badge("Pass 18", "secondary")
    elif booking.deposit:
        deposit = booking.deposit
        if deposit.type == finance_models.DepositType.GRANT_18:
            return format_badge("Ancien Pass 18", "secondary")
        if deposit.type == finance_models.DepositType.GRANT_15_17:
            return format_badge("Ancien Pass 15-17", "secondary")
    return "Aucune information"


def format_active_deposit(deposit: finance_models.Deposit | None) -> str:
    if deposit:
        if not deposit.expirationDate or deposit.expirationDate > date_utils.get_naive_utc_now():
            return Markup('<span class="visually-hidden">Oui</span><i class="bi bi-check-circle-fill"></i>')
    return Markup('<span class="visually-hidden">Non</span><i class="bi bi-x-circle-fill"></i>')


def empty_string_if_null(data: typing.Any | None) -> str:
    if data is None:
        return ""
    return str(data)


def format_date(
    data: datetime.date | datetime.datetime | None,
    strformat: str = "%d/%m/%Y",
    address: geography_models.Address | None = None,
) -> str:
    if not data:
        return ""

    if isinstance(data, datetime.datetime):
        tz = pytz.timezone(address.timezone) if address else PARIS_TZ
        try:
            hours_offset = int(data.astimezone(tz).utcoffset().total_seconds() / 3600)  # type: ignore[union-attr]
        except AttributeError:
            hours_offset = 0
        adjusted_dt = data + datetime.timedelta(hours=hours_offset)
        return adjusted_dt.strftime(strformat)
    return data.strftime(strformat)


def format_date_time(
    data: datetime.date | datetime.datetime | None, address: geography_models.Address | None = None
) -> str:
    local_date_time = format_date(data, strformat="%d/%m/%Y à %Hh%M", address=address)

    if not local_date_time or not address or address.timezone == METROPOLE_TIMEZONE:
        return local_date_time

    split_timezone = address.timezone.split("/")
    paris_date_time = format_date(data, strformat="%d/%m à %Hh%M")
    if paris_date_time[:5] == local_date_time[:5]:
        paris_date_time = paris_date_time[-5:]

    return Markup(
        "{date_and_time}&nbsp;"
        '<i class="bi bi-clock-history text-body" data-bs-toggle="tooltip" data-bs-placement="top"'
        ' data-bs-title="Fuseau horaire : {timezone} ({paris_time}&nbsp;à&nbsp;Paris)"></i>'
    ).format(date_and_time=local_date_time, timezone=split_timezone[-1], paris_time=paris_date_time)


def format_string_to_date_time(data: str) -> str:
    return format_date(datetime.datetime.fromisoformat(data), strformat="%d/%m/%Y à %Hh%M")


def format_cutoff_date(cutoff: datetime.datetime, strformat: str = "%d/%m/%Y") -> str:
    start_period, end_period = finance_api.get_invoice_period(cutoff)
    return f"Réservations validées entre le {start_period.strftime(strformat)} et le {end_period.strftime(strformat)}"


def format_timespan(timespan: psycopg2.extras.DateTimeRange) -> str:
    if not timespan:
        return ""
    start = pytz.utc.localize(timespan.lower).astimezone(finance_utils.ACCOUNTING_TIMEZONE).strftime("%d/%m/%Y")
    if timespan.upper:
        # upper bound is exclusive, and we want to show the last day included in the date range
        end = (
            pytz.utc.localize(timespan.upper - datetime.timedelta(microseconds=1))
            .astimezone(finance_utils.ACCOUNTING_TIMEZONE)
            .strftime("%d/%m/%Y")
        )
    else:
        end = "∞"
    return f"{start} → {end}"


def format_datespan(datespan: psycopg2.extras.DateRange) -> str:
    if not datespan:
        return ""
    start = datespan.lower.strftime("%d/%m/%Y")
    if datespan.upper:
        # upper bound is exclusive, and we want to show the last day included in the date range
        end = (datespan.upper - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    else:
        end = "∞"

    if start == end:
        return start

    return f"{start} → {end}"


def format_timezone(address: geography_models.Address) -> str:
    return address.timezone.rsplit("/", 1)[-1]


def format_amount(
    amount: float | decimal.Decimal | None,
    target: users_models.User | offerers_models.Offerer | offerers_models.Venue | None = None,
) -> str:
    if amount is None:
        amount = 0.0

    display = Markup('<span class="text-nowrap">{formatted_amount}</span>').format(
        formatted_amount=finance_utils.format_currency_for_backoffice(amount)
    )

    if target is not None and target.is_caledonian:
        display += Markup(' <span class="text-nowrap text-muted">({formatted_amount})</span>').format(
            formatted_amount=finance_utils.format_currency_for_backoffice(amount, use_xpf=True)
        )

    return display


def format_cents(
    amount_in_cents: int | None,
    target: users_models.User | offerers_models.Offerer | offerers_models.Venue | None = None,
) -> str:
    if amount_in_cents is None:
        amount_in_cents = 0

    return format_amount(finance_utils.cents_to_full_unit(amount_in_cents), target=target)


def format_count(number: int) -> str:
    return "{:,}".format(number).replace(",", "\u202f")


def format_rate(rate: float | None, display_percent_sign: bool = True) -> str:
    if rate is None:
        return "N/A"

    return f"{rate}\u202f{'%' if display_percent_sign else ''}".replace(".", ",")


def format_rate_multiply_by_100(rate: float | None) -> str:
    if rate is None:
        return ""

    return f"{rate * 100:.2f} %".replace(".", ",")


def format_bool(data: bool | None, none_display: str = "") -> str:
    if data is None:
        return none_display

    if data:
        return "Oui"
    return "Non"


def format_bool_badge(data: bool | None, none_display: str = "") -> str:
    if data is None:
        return none_display

    if data:
        return format_badge("Oui", "success")
    return format_badge("Non", "danger")


def format_string_list(data: list[str] | None, max_characters: int | None = None) -> str:
    if data is None:
        return ""
    result = ", ".join(data)
    if max_characters and len(result) > max_characters:
        result = result[:max_characters].rsplit(",", 1)[0] + "…"
    return result


def pluralize(count: int | None, singular: str = "", plural: str = "s") -> str:
    return plural if count and count > 1 else singular


def genderize(text: str, civility: str | None) -> str:
    if civility == users_models.GenderEnum.M.value:
        return text
    if civility == users_models.GenderEnum.F.value:
        return text + "e"
    return text + "(e)"


def format_gender(gender: users_models.GenderEnum) -> str:
    match gender:
        case users_models.GenderEnum.M:
            return "Monsieur"
        case users_models.GenderEnum.F:
            return "Madame"
        case _:
            return gender.value


def format_reason_label(reason: str | None) -> str:
    if reason:
        return users_constants.SUSPENSION_REASON_CHOICES.get(
            users_constants.SuspensionReason(reason), "Raison inconnue"
        )
    return ""


def format_offerer_rejection_reason(rejection_reason: offerers_models.OffererRejectionReason | str) -> str:
    match rejection_reason:
        case (
            offerers_models.OffererRejectionReason.ELIGIBILITY | offerers_models.OffererRejectionReason.ELIGIBILITY.name
        ):
            return "Non éligible"
        case offerers_models.OffererRejectionReason.ERROR | offerers_models.OffererRejectionReason.ERROR.name:
            return "Erreur jeune ou établissement scolaire"
        case (
            offerers_models.OffererRejectionReason.ADAGE_DECLINED
            | offerers_models.OffererRejectionReason.ADAGE_DECLINED.name
        ):
            return "Refus ADAGE"
        case (
            offerers_models.OffererRejectionReason.OUT_OF_TIME | offerers_models.OffererRejectionReason.OUT_OF_TIME.name
        ):
            return "Non réponse aux questionnaires"
        case (
            offerers_models.OffererRejectionReason.NON_RECEIVED_DOCS
            | offerers_models.OffererRejectionReason.NON_RECEIVED_DOCS.name
        ):
            return "Non réception des documents"
        case (
            offerers_models.OffererRejectionReason.CLOSED_BUSINESS
            | offerers_models.OffererRejectionReason.CLOSED_BUSINESS.name
        ):
            return "SIREN caduc"
        case offerers_models.OffererRejectionReason.OTHER | offerers_models.OffererRejectionReason.OTHER.name:
            return "Autre"
        case _:
            return rejection_reason


def format_booking_cancellation(
    reason: bookings_models.BookingCancellationReasons | educational_models.CollectiveBookingCancellationReasons | None,
    author: users_models.User | None = None,
) -> str:
    match reason:
        case (
            bookings_models.BookingCancellationReasons.OFFERER
            | educational_models.CollectiveBookingCancellationReasons.OFFERER
        ):
            if author:
                return Markup(
                    'Annulée par l\'acteur culturel (<a class="link-primary" href="{url}">{email}</a>)'
                ).format(
                    url=url_for("backoffice_web.pro_user.get", user_id=author.id),
                    email=author.email,
                )
            return "Annulée par l'acteur culturel"
        case (
            bookings_models.BookingCancellationReasons.OFFERER_CONNECT_AS
            | educational_models.CollectiveBookingCancellationReasons.OFFERER_CONNECT_AS
        ):
            if author:
                return Markup('Annulée par <a class="link-primary" href="{url}">{full_name}</a> via Connect As').format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée via Connect As"
        case (
            bookings_models.BookingCancellationReasons.BENEFICIARY
            | educational_models.CollectiveBookingCancellationReasons.BENEFICIARY
        ):
            return "Annulée par le bénéficiaire"
        case (
            bookings_models.BookingCancellationReasons.EXPIRED
            | educational_models.CollectiveBookingCancellationReasons.EXPIRED
        ):
            return "Expirée"
        case (
            bookings_models.BookingCancellationReasons.FRAUD
            | educational_models.CollectiveBookingCancellationReasons.FRAUD
        ):
            return "Fraude avérée"
        case (
            bookings_models.BookingCancellationReasons.FRAUD_SUSPICION
            | educational_models.CollectiveBookingCancellationReasons.FRAUD_SUSPICION
        ):
            return "Suspicion de fraude"
        case (
            bookings_models.BookingCancellationReasons.FRAUD_INAPPROPRIATE
            | educational_models.CollectiveBookingCancellationReasons.FRAUD_INAPPROPRIATE
        ):
            return "Offre non conforme"
        case (
            educational_models.CollectiveBookingCancellationReasons.FINANCE_INCIDENT
            | bookings_models.BookingCancellationReasons.FINANCE_INCIDENT
        ):
            return "Incident finance"
        case (
            educational_models.CollectiveBookingCancellationReasons.BACKOFFICE
            | bookings_models.BookingCancellationReasons.BACKOFFICE
        ):
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a>'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice"
        case (
            educational_models.CollectiveBookingCancellationReasons.BACKOFFICE_EVENT_CANCELLED
            | bookings_models.BookingCancellationReasons.BACKOFFICE_EVENT_CANCELLED
        ):
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a> pour annulation d’évènement'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice pour annulation d’évènement"
        case bookings_models.BookingCancellationReasons.BACKOFFICE_OVERBOOKING:
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a> pour surbooking'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice pour surbooking"
        case bookings_models.BookingCancellationReasons.BACKOFFICE_BENEFICIARY_REQUEST:
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a> sur demande du bénéficiaire'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice sur demande du bénéficiaire"
        case (
            educational_models.CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_MODIFIED
            | bookings_models.BookingCancellationReasons.BACKOFFICE_OFFER_MODIFIED
        ):
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a> pour modification des informations de l\'offre'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice pour modification des informations de l'offre"
        case (
            educational_models.CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_WITH_WRONG_INFORMATION
            | bookings_models.BookingCancellationReasons.BACKOFFICE_OFFER_WITH_WRONG_INFORMATION
        ):
            if author:
                return Markup(
                    "Annulée depuis le backoffice par <a class='link-primary' href=\"{url}\">{full_name}</a> pour erreur d'information dans l'offre"
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice pour erreur d'information dans l'offre"
        case (
            bookings_models.BookingCancellationReasons.BACKOFFICE_OFFERER_BUSINESS_CLOSED
            | educational_models.CollectiveBookingCancellationReasons.BACKOFFICE_OFFERER_BUSINESS_CLOSED
        ):
            if author:
                return Markup(
                    'Annulée depuis le backoffice par <a class="link-primary" href="{url}">{full_name}</a> pour cause de fermeture d\'entité juridique'
                ).format(
                    url=url_for("backoffice_web.bo_users.get_bo_user", user_id=author.id),
                    full_name=author.full_name,
                )
            return "Annulée depuis le backoffice pour cause de fermeture d'entité juridique"
        case (
            bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
            | educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        ):
            return "Refusée par l'institution"
        case educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER:
            return "Refusée par le chef d'établissement"
        case educational_models.CollectiveBookingCancellationReasons.PUBLIC_API:
            return "Refusée sur l'API publique"
        case (
            bookings_models.BookingCancellationReasons.OFFERER_CLOSED
            | educational_models.CollectiveBookingCancellationReasons.OFFERER_CLOSED
        ):
            return "Fermeture de l'entité juridique"
        case None:
            return ""
        case _:
            return reason.value


def format_booking_status_long(booking: bookings_models.Booking | educational_models.CollectiveBooking) -> str:
    if booking.status in (
        bookings_models.BookingStatus.REIMBURSED,
        educational_models.CollectiveBookingStatus.REIMBURSED,
    ):
        return format_badge("AC remboursé", "success")
    if booking.status in (
        bookings_models.BookingStatus.CANCELLED,
        educational_models.CollectiveBookingStatus.CANCELLED,
    ):
        return format_badge("L'offre n'a pas eu lieu", "danger")
    if booking.status in (bookings_models.BookingStatus.USED, educational_models.CollectiveBookingStatus.USED):
        return format_badge("Le jeune a consommé l'offre", "success")
    if isinstance(booking, bookings_models.Booking) and booking.isConfirmed:
        return format_badge("Le jeune ne peut plus annuler", "success")
    if (
        isinstance(booking, educational_models.CollectiveBooking)
        and booking.status == educational_models.CollectiveBookingStatus.CONFIRMED
    ):
        return format_badge("Le chef d'établissement a validé la réservation", "success")
    if booking.status == educational_models.CollectiveBookingStatus.PENDING:
        return format_badge("L'enseignant a posé une option", "success")
    return format_badge("Le jeune a réservé l'offre", "success")


def format_booking_validation_author_type(
    validationAuthorType: bookings_models.BookingValidationAuthorType | None,
) -> str:
    match validationAuthorType:
        case bookings_models.BookingValidationAuthorType.OFFERER:
            return "Partenaire culturel"
        case bookings_models.BookingValidationAuthorType.BACKOFFICE:
            return "Backoffice"
        case bookings_models.BookingValidationAuthorType.AUTO:
            return "Automatique"
        case _:
            return ""


def format_booking_status(
    booking: bookings_models.Booking | educational_models.CollectiveBooking, with_badge: bool = False
) -> str:
    if booking.status in (
        bookings_models.BookingStatus.REIMBURSED,
        educational_models.CollectiveBookingStatus.REIMBURSED,
    ):
        return format_badge("Remboursée", "success") if with_badge else "Remboursée"
    if booking.status in (
        bookings_models.BookingStatus.CANCELLED,
        educational_models.CollectiveBookingStatus.CANCELLED,
    ):
        return format_badge("Annulée", "danger") if with_badge else "Annulée"
    if booking.status in (bookings_models.BookingStatus.USED, educational_models.CollectiveBookingStatus.USED):
        return format_badge("Validée", "success") if with_badge else "Validée"
    if isinstance(booking, bookings_models.Booking) and booking.isConfirmed:
        return "Confirmée"
    if (
        isinstance(booking, educational_models.CollectiveBooking)
        and booking.status == educational_models.CollectiveBookingStatus.CONFIRMED
    ):
        return "Confirmée"
    if booking.status == educational_models.CollectiveBookingStatus.PENDING:
        return Markup('<span class="text-nowrap">Pré-réservée</span>') if with_badge else "Pré-réservée"
    return "Réservée"


def format_validation_status(status: validation_status_mixin.ValidationStatus) -> str:
    match status:
        case validation_status_mixin.ValidationStatus.NEW:
            return "Nouveau"
        case validation_status_mixin.ValidationStatus.PENDING:
            return "En attente"
        case validation_status_mixin.ValidationStatus.VALIDATED:
            return "Validé"
        case validation_status_mixin.ValidationStatus.REJECTED:
            return "Rejeté"
        case validation_status_mixin.ValidationStatus.DELETED:
            return "Supprimé"
        case validation_status_mixin.ValidationStatus.CLOSED:
            return "Fermé"
        case _:
            return status.value


def format_withdrawal_type(withdrawal_type: offers_models.WithdrawalTypeEnum | None) -> str:
    match withdrawal_type:
        case offers_models.WithdrawalTypeEnum.BY_EMAIL:
            return "Par email"
        case offers_models.WithdrawalTypeEnum.IN_APP:
            return "Dans l'app"
        case offers_models.WithdrawalTypeEnum.NO_TICKET:
            return "Sans ticket"
        case offers_models.WithdrawalTypeEnum.ON_SITE:
            return "Sur place"
        case None:
            return ""
        case _:
            return withdrawal_type.value


def format_badge(text: str, category: str = "primary", icon: str | None = None) -> str:
    # Category: primary, secondary, success, danger, warning and info
    span_class = f"badge text-{category} bg-{category}-subtle"
    if icon:
        return Markup(
            '<span class="{span_class} d-inline-flex gap-1"><i class="bi bi-{icon}"></i>{text}</span>'
        ).format(text=text, span_class=span_class, icon=icon)
    return Markup('<span class="{span_class}">{text}</span>').format(text=text, span_class=span_class)


def format_offer_validation_status(status: offer_mixin.OfferValidationStatus, with_badge: bool = False) -> str:
    prefix = "\u2022\u00a0"  # bullet(•) + no-break space
    match status:
        case offer_mixin.OfferValidationStatus.DRAFT:
            return format_badge(f"{prefix}Nouvelle", "info") if with_badge else "Nouvelle"
        case offer_mixin.OfferValidationStatus.PENDING:
            return format_badge(f"{prefix}En attente", "warning") if with_badge else "En attente"
        case offer_mixin.OfferValidationStatus.APPROVED:
            return format_badge(f"{prefix}Validée", "success") if with_badge else "Validée"
        case offer_mixin.OfferValidationStatus.REJECTED:
            return format_badge(f"{prefix}Rejetée", "danger") if with_badge else "Rejetée"
        case _:
            return status.value


def format_product_cgu_compatibility_status(
    cgu_compatibility: offers_models.GcuCompatibilityType, provider_name: str | None, with_badge: bool = False
) -> str:
    prefix = "\u2022\u00a0"  # bullet(•) + no-break space
    match cgu_compatibility:
        case offers_models.GcuCompatibilityType.COMPATIBLE:
            return format_badge(f"{prefix}Compatible", "success") if with_badge else "Compatible"
        case offers_models.GcuCompatibilityType.FRAUD_INCOMPATIBLE:
            return (
                format_badge(f"{prefix}Incompatible (Fraude & Conformité)", "danger")
                if with_badge
                else "Incompatible (Fraude & Conformité)"
            )
        case offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE:
            return (
                format_badge(f"{prefix}Incompatible (Provider)", "danger") if with_badge else "Incompatible (Provider)"
            )
        case _:
            return cgu_compatibility.value


def format_artist_visibility_status(is_blacklisted: bool) -> str:
    if is_blacklisted:
        text = "Non visible"
        category = "danger"
    else:
        text = "Visible"
        category = "success"
    return format_badge(text=text, category=category)


def format_offer_status(status: offer_mixin.OfferStatus) -> str:
    match status:
        case offer_mixin.OfferStatus.DRAFT:
            return "Brouillon"
        case offer_mixin.OfferStatus.SCHEDULED:
            return "Programmée"
        case offer_mixin.OfferStatus.PUBLISHED:
            return "Publiée non réservable"
        case offer_mixin.OfferStatus.ACTIVE:
            return "Publiée réservable"
        case offer_mixin.OfferStatus.PENDING:
            return "En instruction"
        case offer_mixin.OfferStatus.EXPIRED:
            return "Expirée"
        case offer_mixin.OfferStatus.REJECTED:
            return "Non conforme"
        case offer_mixin.OfferStatus.SOLD_OUT:
            return "Épuisée"
        case offer_mixin.OfferStatus.INACTIVE:
            return "En pause"
        case _:
            return status.value


def format_offer_category(subcategory_id: str) -> str:
    subcategory = ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if subcategory:
        return subcategory.category.pro_label
    return ""


def format_offer_subcategory(subcategory_id: str) -> str:
    subcategory = ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if subcategory:
        return subcategory.pro_label
    return ""


def format_collective_offer_formats(formats: typing.Sequence[EacFormat] | None) -> str:
    if not formats:
        return ""
    try:
        return ", ".join([fmt.value for fmt in formats])
    except Exception:
        return "<inconnus>"


def format_subcategories(subcategories: list[str]) -> str:
    if subcategories == []:
        return ""
    labels = sorted(ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label for subcategory_id in subcategories)
    displayed_labels = ", ".join(labels)
    return displayed_labels


def format_collective_offer_rejection_reason(reason: educational_models.CollectiveOfferRejectionReason) -> str:
    match reason:
        case educational_models.CollectiveOfferRejectionReason.CO_FUNDING:
            return "Tarif global/Co-financement"
        case educational_models.CollectiveOfferRejectionReason.CSTI_IRRELEVANT:
            return "Ne relève pas de la CSTI"
        case educational_models.CollectiveOfferRejectionReason.EXAMS_PREPARATION:
            return "Préparation aux examens"
        case educational_models.CollectiveOfferRejectionReason.HOUSING_CATERING_TRANSPORT:
            return "Restauration/Hébergement/Transport"
        case educational_models.CollectiveOfferRejectionReason.INELIGIBLE_OFFER:
            return "Offre inéligible"
        case educational_models.CollectiveOfferRejectionReason.INELIGIBLE_SERVICE:
            return "Prestation inéligible"
        case educational_models.CollectiveOfferRejectionReason.MAX_BUDGET_REACHED:
            return "Budget maximal atteint"
        case educational_models.CollectiveOfferRejectionReason.MISSING_DESCRIPTION:
            return "Description manquante"
        case educational_models.CollectiveOfferRejectionReason.MISSING_DESCRIPTION_AND_DATE:
            return "Date et description manquante"
        case educational_models.CollectiveOfferRejectionReason.MISSING_MEDIATION:
            return "Mediation manquante"
        case educational_models.CollectiveOfferRejectionReason.MISSING_PRICE:
            return "Prix manquant"
        case educational_models.CollectiveOfferRejectionReason.OTHER:
            return "Autre"
        case educational_models.CollectiveOfferRejectionReason.PAST_DATE_OFFER:
            return "Offre anti-datée"
        case educational_models.CollectiveOfferRejectionReason.PRIMARY_ELEMENTARY_SCHOOL:
            return "Offre maternelle/primaire"
        case educational_models.CollectiveOfferRejectionReason.WRONG_DATE:
            return "Date erronée"
        case educational_models.CollectiveOfferRejectionReason.WRONG_PRICE:
            return "Tarif erroné"
        case _:
            return reason.value


def format_fraud_review_status(status: subscription_models.FraudReviewStatus) -> str:
    match status:
        case subscription_models.FraudReviewStatus.OK:
            return "OK"
        case subscription_models.FraudReviewStatus.KO:
            return "KO"
        case subscription_models.FraudReviewStatus.REDIRECTED_TO_DMS:
            return "Redirigé vers Démarche Numérique"
        case _:
            return status.value


def format_dms_status(status: str) -> str:
    match status:
        case "accepte":
            return "Accepté"
        case "en_instruction":
            return "En instruction"
        case "en_construction":
            return "En construction"
        case "refuse":
            return "Refusé"
        case "sans_suite":
            return "Classé sans suite"
        case "a_corriger":
            return "À corriger"
        case _:
            return status


def format_dms_application_status(
    status: GraphQLApplicationStates | finance_models.BankAccountApplicationStatus,
) -> str:
    match status:
        case GraphQLApplicationStates.accepted | finance_models.BankAccountApplicationStatus.ACCEPTED:
            return "Accepté"
        case GraphQLApplicationStates.on_going | finance_models.BankAccountApplicationStatus.ON_GOING:
            return "En instruction"
        case GraphQLApplicationStates.draft | finance_models.BankAccountApplicationStatus.DRAFT:
            return "En construction"
        case GraphQLApplicationStates.refused | finance_models.BankAccountApplicationStatus.REFUSED:
            return "Refusé"
        case (
            GraphQLApplicationStates.without_continuation
            | finance_models.BankAccountApplicationStatus.WITHOUT_CONTINUATION
        ):
            return "Classé sans suite"
        case finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS:
            return "À corriger"
        case _:
            return status.value


def format_dms_application_status_badge(
    status: GraphQLApplicationStates | finance_models.BankAccountApplicationStatus | str,
) -> str:
    if isinstance(status, str):
        status = GraphQLApplicationStates(status)

    match status:
        case GraphQLApplicationStates.accepted | finance_models.BankAccountApplicationStatus.ACCEPTED:
            return format_badge("Accepté", "success")
        case GraphQLApplicationStates.on_going | finance_models.BankAccountApplicationStatus.ON_GOING:
            return format_badge("En instruction", "secondary")
        case GraphQLApplicationStates.draft | finance_models.BankAccountApplicationStatus.DRAFT:
            return format_badge("En construction", "info")
        case GraphQLApplicationStates.refused | finance_models.BankAccountApplicationStatus.REFUSED:
            return format_badge("Refusé", "danger")
        case (
            GraphQLApplicationStates.without_continuation
            | finance_models.BankAccountApplicationStatus.WITHOUT_CONTINUATION
        ):
            return format_badge("Classé sans suite", "primary")
        case finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS:
            return format_badge("À corriger", "warning")
        case _:
            return status.value


def format_user_account_update_flag(flag: users_models.UserAccountUpdateFlag) -> str:
    match flag:
        case users_models.UserAccountUpdateFlag.MISSING_VALUE:
            return "Saisie incomplète"
        case users_models.UserAccountUpdateFlag.INVALID_VALUE:
            return "Saisie invalide"
        case users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL:
            return "Email en doublon"
        case users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION:
            return "En attente de correction"
        case users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED:
            return "Corrigé"
        case _:
            return flag.value


def format_user_account_update_flags(flags: typing.Iterable[users_models.UserAccountUpdateFlag]) -> str:
    badges = []
    for flag in flags:
        match flag:
            case users_models.UserAccountUpdateFlag.MISSING_VALUE:
                badges.append(format_badge("Saisie incomplète", "warning", "exclamation-triangle"))
            case users_models.UserAccountUpdateFlag.INVALID_VALUE:
                badges.append(format_badge("Saisie invalide", "warning", "exclamation-triangle"))
            case users_models.UserAccountUpdateFlag.DUPLICATE_NEW_EMAIL:
                badges.append(format_badge("Email en doublon", "primary", "person-plus-fill"))
            case users_models.UserAccountUpdateFlag.WAITING_FOR_CORRECTION:
                badges.append(format_badge("En attente de correction", "warning"))
            case users_models.UserAccountUpdateFlag.CORRECTION_RESOLVED:
                badges.append(format_badge("Corrigé", "secondary"))
            case _:
                badges.append(format_badge(flag.value, "secondary"))
    return Markup("").join(badges)


def format_user_account_update_type(update_type: users_models.UserAccountUpdateType) -> str:
    match update_type:
        case users_models.UserAccountUpdateType.EMAIL:
            return "Email"
        case users_models.UserAccountUpdateType.PHONE_NUMBER:
            return "Numéro de téléphone"
        case users_models.UserAccountUpdateType.FIRST_NAME:
            return "Prénom"
        case users_models.UserAccountUpdateType.LAST_NAME:
            return "Nom"
        case users_models.UserAccountUpdateType.LOST_CREDENTIALS:
            return "Perte de l'identifiant"
        case users_models.UserAccountUpdateType.ACCOUNT_HAS_SAME_INFO:
            return "Compte a les mêmes infos"
        case _:
            return update_type.value


def format_registration_step_description(description: str) -> str:
    description = format_subscription_step(description)
    description = format_eligibility_value(description)
    return description


def format_subscription_step(step_value: str) -> str:
    match step_value.lower():
        case "email-validation":
            return "Email"
        case "phone-validation":
            return "Num. téléphone"
        case "profile-completion":
            return "Profil complet"
        case "identity-check":
            return "ID check"
        case "honor-statement":
            return "Attestation sur l'honneur"
        case _:
            return step_value


def format_eligibility_value(tunnel_type: str) -> str:
    match tunnel_type.lower():
        case "underage":
            return "Ancien Pass 15-17"
        case "underage+age-18-old":
            return "Ancien Pass 15-17+18 (ancien)"
        case "underage+age-18":
            return "Ancien Pass 15-17+18"
        case "underage+age-17":
            return "Pass 15-17+17"
        case "underage+age-17-18":
            return "Pass 15-17+17-18"
        case "age-18-old":
            return "Ancien Pass 18"
        case "age-17":
            return "Pass 17"
        case "age-18":
            return "Pass 18"
        case "age-17-18":
            return "Pass 17+Pass 18"
        case "not-eligible":
            return "Non éligible"
        case _:
            return tunnel_type


def format_eligibility_type(eligibility_type: users_models.EligibilityType) -> str:
    match eligibility_type:
        case users_models.EligibilityType.UNDERAGE:
            return "Ancien Pass 15-17"
        case users_models.EligibilityType.AGE18:
            return "Ancien Pass 18"
        case users_models.EligibilityType.AGE17_18:
            return "Pass 17-18"
        case users_models.EligibilityType.FREE:
            return "Pass 15-16"
        case _:
            return eligibility_type.value


def format_as_badges(items: list[str] | None, return_markup: bool = True) -> str:
    if not items:
        return ""

    return (Markup(" ") if return_markup else " ").join(format_badge(item, "secondary") for item in items)


def format_tag_object_list(
    objects_with_label_attribute: list[offerers_models.OffererTag] | list[offerers_models.OffererTagCategory],
) -> str:
    if objects_with_label_attribute:
        return format_as_badges(
            [getattr(obj, "label", getattr(obj, "name", "")) for obj in objects_with_label_attribute]
        )
    return ""


def format_criteria(criteria: list[criteria_models.Criterion]) -> str:
    return format_as_badges([criterion.name for criterion in criteria])


def format_compliance_reason(feature: str) -> str:
    match feature:
        case "offer_name":
            return "Nom de l'offre"
        case "offer_description":
            return "Description de l'offre"
        case "offer_subcategory_id" | "offer_subcategoryid":
            return "Sous-catégorie"
        case "rayon":
            return "Rayon"
        case "macro_rayon":
            return "Macro-rayon"
        case "stock_price":
            return "Prix"
        case "image_embedding":
            return "Image de l'offre"
        case "semantic_content_embedding":
            return "Nom et description de l'offre"
        case _:
            return feature


def format_compliance_reasons(features: list[str], return_markup: bool = True) -> str:
    return format_as_badges([format_compliance_reason(feature) for feature in features], return_markup=return_markup)


def format_offer_compliance_llm_validation(
    validation_status_prediction: offers_models.ComplianceValidationStatusPrediction,
) -> str:
    match validation_status_prediction:
        case offers_models.ComplianceValidationStatusPrediction.APPROVED:
            return format_badge("À valider", "success")
        case offers_models.ComplianceValidationStatusPrediction.REJECTED:
            return format_badge("À rejeter", "warning")
        case _:
            return validation_status_prediction.value


def format_confidence_level(confidence_level: offerers_models.OffererConfidenceLevel | None) -> str:
    match confidence_level:
        case offerers_models.OffererConfidenceLevel.MANUAL_REVIEW:
            return "Revue manuelle de toutes les offres"
        case offerers_models.OffererConfidenceLevel.WHITELIST:
            return "Validation automatique (liste blanche)"
        case None:
            return "Suivre les règles"

    return confidence_level


def format_offerer_status_badge(offerer: offerers_models.Offerer) -> str:
    if offerer.isNew:
        return format_badge("Nouvelle", "info")
    if offerer.isPending:
        return format_badge("En attente", "warning")
    if offerer.isValidated:
        return format_badge("Validée", "success")
    if offerer.isRejected:
        return format_badge("Rejetée", "danger")
    if offerer.isDeleted:
        return format_badge("Supprimée", "danger")
    if offerer.isClosed:
        return format_badge("Fermée", "danger")
    return ""


def format_user_offerer_status_badge(user_offerer: offerers_models.UserOfferer) -> str:
    if user_offerer.isNew:
        return format_badge("Nouveau", "info")
    if user_offerer.isPending:
        return format_badge("En attente", "warning")
    if user_offerer.isValidated:
        return format_badge("Validé", "success")
    if user_offerer.isRejected:
        return format_badge("Rejeté", "danger")
    if user_offerer.isDeleted:
        return format_badge("Supprimé", "danger")
    if user_offerer.isClosed:
        return format_badge("Fermé", "danger")
    return ""


def format_confidence_level_badge(
    confidence_level: offerers_models.OffererConfidenceLevel | str | None, show_no_rule: bool = False, info: str = ""
) -> str:
    match confidence_level:
        case (
            offerers_models.OffererConfidenceLevel.MANUAL_REVIEW
            | offerers_models.OffererConfidenceLevel.MANUAL_REVIEW.value
        ):
            return format_badge(f"Revue manuelle {info}", "warning")
        case offerers_models.OffererConfidenceLevel.WHITELIST | offerers_models.OffererConfidenceLevel.WHITELIST.value:
            return format_badge(f"Validation auto {info}", "success")

    if show_no_rule:
        return format_badge("Suivre les règles", "secondary")

    return ""


def format_confidence_level_badge_for_venue(venue: offerers_models.Venue) -> str:
    if venue.confidenceLevel:
        return format_confidence_level_badge(venue.confidenceLevel)

    return format_confidence_level_badge(
        venue.managingOfferer.confidenceLevel, show_no_rule=True, info="(entité juridique)"
    )


def format_fraud_check_url(id_check_item: serialization_accounts.IdCheckItemModel) -> str:
    if id_check_item.type == subscription_models.FraudCheckType.UBBLE.value:
        if ubble_api.is_v2_identification(id_check_item.thirdPartyId):
            return f"https://dashboard.ubble.ai/identity-verifications/{id_check_item.thirdPartyId}"
        return f"https://dashboard.ubble.ai/identifications/{id_check_item.thirdPartyId}"
    if id_check_item.type == subscription_models.FraudCheckType.DMS.value and id_check_item.technicalDetails:
        return f"https://demarche.numerique.gouv.fr/procedures/{id_check_item.technicalDetails['procedure_number']}/dossiers/{id_check_item.thirdPartyId}"
    return ""


def format_fraud_action_dict_url(fraud_action_dict: dict) -> str:
    if fraud_action_dict["type"] == subscription_models.FraudCheckType.UBBLE.value:
        if ubble_api.is_v2_identification(fraud_action_dict["techId"]):
            return f"https://dashboard.ubble.ai/identity-verifications/{fraud_action_dict['techId']}"
        return f"https://dashboard.ubble.ai/identifications/{fraud_action_dict['techId']}"
    if (
        fraud_action_dict["type"] == subscription_models.FraudCheckType.DMS.value
        and fraud_action_dict["technicalDetails"]
    ):
        return f"https://demarche.numerique.gouv.fr/procedures/{fraud_action_dict['technicalDetails']['procedure_number']}/dossiers/{fraud_action_dict['techId']}"
    return ""


def format_gdpr_date_processed(date_processed: datetime.datetime | None) -> str:
    return "prête" if date_processed else "en attente"


def _format_modified_info_value(value: typing.Any, name: str | None = None, field_type: typing.Any = None) -> str:
    if name == "venueTypeCode":
        try:
            value = offerers_models.VenueTypeCode[value].value
        except KeyError:
            pass  # in case of an old type code removed from enum

    if name == "confidenceRule.confidenceLevel":
        try:
            return format_confidence_level_badge(offerers_models.OffererConfidenceLevel[value])
        except KeyError:
            pass  # in case of an old type code removed from enum

    if isinstance(value, list):
        return format_string_list(value)
    if isinstance(value, bool):
        return format_bool(value)
    if field_type is not None and field_type is datetime.datetime:
        parsed_value = None
        try:
            parsed_value = datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError):
            pass
        return format_date_time(parsed_value)
    return str(value)


def format_pivot_name(pivot_name: str) -> str:
    match pivot_name:
        case "allocine":
            return "Allociné"
        case "boost":
            return "Boost"
        case "cgr":
            return "CGR"
        case "cineoffice":
            return "Ciné Office"
        case "ems":
            return "EMS"
        case _:
            return pivot_name


def format_modified_info_values(
    modified_info: typing.Any, name: str | None = None, model_instance: typing.Any = None
) -> str:
    old_info = modified_info.get("old_info")
    new_info = modified_info.get("new_info")

    field_type = None
    if model_instance:
        field = model_instance.__table__.columns.get(name)
        if field is not None:
            field_type = field.type.python_type

    if old_info is not None and new_info is not None:
        return Markup("{old_value} → {new_value}").format(
            old_value=_format_modified_info_value(old_info, name, field_type),
            new_value=_format_modified_info_value(new_info, name, field_type),
        )

    if old_info is not None:
        return Markup("suppression de : {value}").format(value=_format_modified_info_value(old_info, name, field_type))

    if new_info is not None:
        return Markup("ajout de : {value}").format(value=_format_modified_info_value(new_info, name, field_type))

    return str(modified_info)  # this should not happen if data is consistent


def format_music_gtl_id(music_gtl_id: str) -> str:
    return next(
        (
            music_genre.label
            for music_genre in pcapi.core.categories.genres.music.TITELIVE_MUSIC_TYPES
            if music_genre.gtl_id[:2] == music_gtl_id[:2]
        ),
        f"Gtl inconnu [{music_gtl_id}]",
    )


def format_show_type(show_type_id: int | str) -> str:
    if show_type_id:
        try:
            return show.SHOW_TYPES_LABEL_BY_CODE.get(int(show_type_id), f"Autre[{show_type_id}]")
        except ValueError:
            return f"Autre[{show_type_id}]"
    return "[Non renseigné]"


def format_show_subtype(show_subtype_id: int | str) -> str:
    if show_subtype_id:
        try:
            return show.SHOW_SUB_TYPES_LABEL_BY_CODE.get(int(show_subtype_id), f"Autre[{show_subtype_id}]")
        except ValueError:
            return f"Autre[{show_subtype_id}]"
    return "[Non renseigné]"


def match_opening_hours(info_name: str) -> str | None:
    day_mapping = {
        "MONDAY": "lundi",
        "TUESDAY": "mardi",
        "WEDNESDAY": "mercredi",
        "THURSDAY": "jeudi",
        "FRIDAY": "vendredi",
        "SATURDAY": "samedi",
        "SUNDAY": "dimanche",
    }
    if match := re.compile(r"^openingHours\.(\w+)\.timespan$").match(info_name):
        day = match.group(1)
        return day_mapping.get(day, day)
    return None


def format_modified_info_name(info_name: str) -> str:
    match info_name:
        case "force_debit_note":
            return "Génération d'une note de débit"
        case "comment":
            return "Commentaire"
        case "email":
            return "Email"
        case "firstName":
            return "Prénom"
        case "lastName":
            return "Nom"
        case "validatedBirthDate":
            return "Date de naissance"
        case "postalCode":
            return "Code postal"
        case "phoneNumber":
            return "Téléphone"
        case "city":
            return "Ville"
        case "street":
            return "Adresse"
        case "banId":
            return "Identifiant Base Adresse Nationale"
        case "bookingEmail":
            return "Email"
        case "contact.email":
            return "Email de contact"
        case "contact.phone_number":
            return "Numéro de téléphone de contact"
        case "contact.social_medias":
            return "Réseaux sociaux de contact"
        case "contact.website":
            return "Site internet de contact"
        case "isPermanent":
            return "Permanent"
        case "name":
            return "Nom juridique"
        case "publicName":
            return "Nom d'usage"
        case "criteria":
            return "Tags"
        case "pricingPointSiret":
            return "Siret de valorisation"
        case "audioDisabilityCompliant":
            return "Accessibilité handicap auditif"
        case "motorDisabilityCompliant":
            return "Accessibilité handicap moteur"
        case "mentalDisabilityCompliant":
            return "Accessibilité handicap psychique"
        case "visualDisabilityCompliant":
            return "Accessibilité handicap visuel"
        case "withdrawalDetails":
            return "Conditions de retrait"
        case "venueLabelId":
            return "ID Label"
        case "venueTypeCode":
            return "Activité principale"
        case "label":
            return "Intitulé"
        case "accessibilityProvider.externalAccessibilityId":
            return "ID chez Acceslibre"
        case "accessibilityProvider.externalAccessibilityUrl":
            return "URL chez Acceslibre"
        case "notificationSubscriptions.marketing_email":
            return "Abonné aux emails marketing"
        case "notificationSubscriptions.marketing_push":
            return "Abonné aux notifications push"
        case "confidenceRule.confidenceLevel":
            return "Validation des offres"
        case "offererAddress.addressId":
            return "Adresse - ID Adresse"
        case "offererAddress.id":
            return "OA ID"
        case "offererAddress.address.inseeCode":
            return "Adresse - Code Insee"
        case "offererAddress.address.city":
            return "Adresse - Ville"
        case "offererAddress.address.postalCode":
            return "Adresse - Code postal"
        case "offererAddress.address.street":
            return "Adresse - Adresse"
        case "offererAddress.address.banId":
            return "Adresse - Identifiant Base Adresse Nationale"
        case "offererAddress.address.latitude":
            return "Adresse - Latitude"
        case "offererAddress.address.longitude":
            return "Adresse - Longitude"
        case "offererAddress.address.isManualEdition":
            return "Adresse - Edition manuelle"
        case "old_oa_label":
            return "Ancien label OA"
        case "isActive":
            return "Actif"
        case "adageId":
            return "ID ADAGE"
        case "isOpenToPublic":
            return "Accueil du public"
        case "campaignDate":
            return "Date"
        case "activity":
            return "Activité principale"

    if day := match_opening_hours(info_name):
        return f"Horaires du {day}"

    return info_name.replace("_", " ").capitalize()


def format_permission_name(permission_name: str) -> str:
    try:
        return perm_models.Permissions[permission_name].value
    except KeyError:
        return permission_name


def format_offer_validation_sub_rule_field(sub_rule_field: offers_models.OfferValidationSubRuleField) -> str:
    match sub_rule_field:
        case offers_models.OfferValidationSubRuleField.OFFER_TYPE:
            return "Le type de l'offre"
        case offers_models.OfferValidationSubRuleField.MAX_PRICE_OFFER:
            return "Le prix max de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.PRICE_COLLECTIVE_STOCK:
            return "Le prix de l'offre collective"
        case offers_models.OfferValidationSubRuleField.PRICE_DETAIL_COLLECTIVE_STOCK:
            return "Les détails de paiement de l'offre collective"
        case offers_models.OfferValidationSubRuleField.PRICE_DETAIL_COLLECTIVE_OFFER_TEMPLATE:
            return "Les détails de paiement de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.WITHDRAWAL_DETAILS_OFFER:
            return "Les modalités de retrait de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.NAME_OFFER:
            return "Le nom de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.NAME_COLLECTIVE_OFFER:
            return "Le nom de l'offre collective"
        case offers_models.OfferValidationSubRuleField.NAME_COLLECTIVE_OFFER_TEMPLATE:
            return "Le nom de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.TEXT_OFFER:
            return "Le nom ou la description de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.TEXT_COLLECTIVE_OFFER:
            return "Le nom, la description ou le détail du prix de l'offre collective"
        case offers_models.OfferValidationSubRuleField.TEXT_COLLECTIVE_OFFER_TEMPLATE:
            return "Le nom, la description ou le détail du prix de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_OFFER:
            return "La description de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_COLLECTIVE_OFFER:
            return "La description de l'offre collective"
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_COLLECTIVE_OFFER_TEMPLATE:
            return "La description de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.SUBCATEGORY_OFFER:
            return "La sous-catégorie de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.CATEGORY_OFFER:
            return "La catégorie de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.SHOW_SUB_TYPE_OFFER:
            return "Le sous-type de spectacle de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.ID_VENUE:
            return "Le partenaire culturel proposant l'offre"
        case offers_models.OfferValidationSubRuleField.ID_OFFERER:
            return "L'entité juridique proposant l'offre"
        case offers_models.OfferValidationSubRuleField.FORMATS_COLLECTIVE_OFFER:
            return "Les formats de l'offre collective"
        case offers_models.OfferValidationSubRuleField.FORMATS_COLLECTIVE_OFFER_TEMPLATE:
            return "Les formats de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.AUTHOR_OFFER:
            return "L'auteur d'une offre individuelle"
        case offers_models.OfferValidationSubRuleField.PUBLISHER_OFFER:
            return "L'éditeur d'une offre individuelle"
        case _:
            return sub_rule_field.value


def format_offer_validation_operator(operator: offers_models.OfferValidationRuleOperator) -> str:
    match operator:
        case offers_models.OfferValidationRuleOperator.EQUALS:
            return "est égal à"
        case offers_models.OfferValidationRuleOperator.NOT_EQUALS:
            return "est différent de"
        case offers_models.OfferValidationRuleOperator.GREATER_THAN:
            return "est supérieur à"
        case offers_models.OfferValidationRuleOperator.GREATER_THAN_OR_EQUAL_TO:
            return "est supérieur ou égal à"
        case offers_models.OfferValidationRuleOperator.LESS_THAN:
            return "est inférieur à"
        case offers_models.OfferValidationRuleOperator.LESS_THAN_OR_EQUAL_TO:
            return "est inférieur ou égal à"
        case offers_models.OfferValidationRuleOperator.IN:
            return "est parmi"
        case offers_models.OfferValidationRuleOperator.NOT_IN:
            return "n'est pas parmi"
        case offers_models.OfferValidationRuleOperator.CONTAINS:
            return "contient"
        case offers_models.OfferValidationRuleOperator.CONTAINS_EXACTLY:
            return "contient exactement"
        case offers_models.OfferValidationRuleOperator.INTERSECTS:
            return "contiennent"
        case offers_models.OfferValidationRuleOperator.NOT_INTERSECTS:
            return "ne contiennent pas"
        case _:
            return operator.value


def format_offer_validation_sub_rule(sub_rule: offers_models.OfferValidationSubRule) -> str:
    try:
        sub_rule_field = offers_models.OfferValidationSubRuleField(
            {
                "model": sub_rule.model,
                "attribute": sub_rule.attribute,
            }
        )
        sub_rule_text = format_offer_validation_sub_rule_field(sub_rule_field)
    except ValueError:
        sub_rule_text = f"{sub_rule.model.value if sub_rule.model else ''}.{sub_rule.attribute.value}"

    sub_rule_text += f" {format_offer_validation_operator(sub_rule.operator)}"
    return sub_rule_text


def format_offer_validation_rule_list(rules: list[offers_models.OfferValidationRule]) -> str:
    return ", ".join(rule.name for rule in rules)


def format_sub_rules_info_type(info: str) -> str:
    match info:
        case "sub_rules_created":
            return "Ajout de sous-règle(s) :"
        case "sub_rules_deleted":
            return "Suppression de sous-règle(s) :"
        case "sub_rules_modified":
            return "Modification de sous-règle(s) :"
        case _:
            return info


def get_comparated_format_function(
    sub_rule: offers_models.OfferValidationSubRule,
    offerer_dict: dict,
    venue_dict: dict,
) -> typing.Callable[[typing.Any], typing.Any]:
    try:
        if (
            sub_rule.attribute == offers_models.OfferValidationAttribute.ID
            and sub_rule.model == offers_models.OfferValidationModel.OFFERER
        ):
            return lambda offerer_id: offerer_dict.get(offerer_id, str(f"Offerer ID : {offerer_id}"))
        if (
            sub_rule.attribute == offers_models.OfferValidationAttribute.ID
            and sub_rule.model == offers_models.OfferValidationModel.VENUE
        ):
            return lambda venue_id: venue_dict.get(venue_id, str(f"Venue ID : {venue_id}"))
        if sub_rule.attribute == offers_models.OfferValidationAttribute.CATEGORY_ID:
            return lambda category_id: pro_categories.ALL_CATEGORIES_DICT[category_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SUBCATEGORY_ID:
            return lambda subcategory_id: ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SHOW_SUB_TYPE:
            return lambda show_sub_type_code: show.SHOW_SUB_TYPES_LABEL_BY_CODE[int(show_sub_type_code)]
        if sub_rule.attribute == offers_models.OfferValidationAttribute.FORMATS:
            return lambda fmt: EacFormat[fmt].value
    except ValueError as err:
        logger.error(
            "Unhandled object in the formatter of the offer validation rules list page",
            extra={"sub_rule_id": sub_rule.id, "error": err},
        )
    return lambda x: x


def format_offer_types(data: list[str]) -> str:
    types = {
        "Offer": "Offre individuelle",
        "CollectiveOffer": "Offre collective",
        "CollectiveOfferTemplate": "Offre collective vitrine",
    }
    return " ou ".join([types[type_name] for type_name in data])


def format_website(website: str) -> str:
    if not re.match(r"^\w+://", website):
        return "https://{}".format(website)
    return website


def format_titelive_id_lectorat(id_lectorat: str) -> str:
    match id_lectorat:
        case "0":
            return "Non précisé"
        case "1":
            return "ENSEIGNANTS"
        case "2":
            return "ELEVES"
        case "3":
            return "Spécialistes"
        case "4":
            return "à partir de 9 ANS"
        case "5":
            return "à partir de 8 ANS"
        case "6":
            return "5/6 ans"
        case "7":
            return "6/7 ans"
        case "8":
            return "7/8 ans"
        case "9":
            return "9/10 ans"
        case "10":
            return "à partir de 1 AN"
        case "11":
            return "à partir de 2 ANS"
        case "12":
            return "à partir de 3 ANS"
        case "13":
            return "à partir de 4 ANS"
        case "14":
            return "à partir de 5 ANS"
        case "15":
            return "à partir de 6 ANS"
        case "16":
            return "à partir de 7 ANS"
        case "17":
            return "à partir de 10 ANS"
        case "18":
            return "à partir de 11 ANS"
        case "19":
            return "à partir de 12 ANS"
        case "20":
            return "à partir de 13 ANS"
        case "21":
            return "7/9 ans"
        case "22":
            return "9/12 ans"
        case "23":
            return "5/7 ans"
        case "24":
            return "3/5 ans"
        case "25":
            return "0/3 ans"
        case "26":
            return "12/16 ans"
        case "27":
            return "à partir de 14 ans"
        case "28":
            return "à partir de 15 ans"
        case "29":
            return "3/4 ans"
        case "30":
            return "8/9 ans"
        case "31":
            return "10/11 ans"
        case "32":
            return "9/11 ans"
        case "33":
            return "à partir de 18 mois"
        case "34":
            return "4/5 ans"
        case "35":
            return "6/9 ans"
        case "36":
            return "Collégiens"
        case "37":
            return "10/12 ans"
        case "38":
            return "Tout public"
        case "39":
            return "Public motivé"
        case "40":
            return "Niveau Bac"
        case "41":
            return "6/10 ans"
        case "42":
            return "Débutants"
        case "43":
            return "Tous niveaux"
        case "44":
            return "Perfectionnement"
        case "45":
            return "+ de 18 ans"
        case "46":
            return "à partir de 16 ans"
        case "47":
            return "14/15 ans"
        case "48":
            return "2/3 ans"
        case "49":
            return "8/10 ans"
        case "50":
            return "3/6 ans"
        case "51":
            return "6/8 ans"
        case "52":
            return "6/12 ans"
        case "53":
            return "8/12 ans"
        case _:
            return f'ID lectorat "{id_lectorat}" non renseigné'


def format_venue_target(target: offerers_models.Target) -> str:
    match target:
        case offerers_models.Target.INDIVIDUAL:
            return "Individuelles"
        case offerers_models.Target.EDUCATIONAL:
            return "Collectives"
        case offerers_models.Target.INDIVIDUAL_AND_EDUCATIONAL:
            return "Indiv. et coll."
        case _:
            return ""


def parse_referrer(url: str) -> str:
    """
    Ensure that a relative path is used, which will be understood.
    Referrer can be modified by the client, therefore cannot be trusted.
    """
    try:
        parsed = urlparse(url)
        return urlunparse(("", "", parsed.path, parsed.params, parsed.query, parsed.fragment))
    except Exception:
        return "/"


def action_to_name(action_url: str) -> str:
    """
    Slugify a form action path to a name so form can be controlled with JS.
    """
    try:
        if len(action_url) != 0:
            return action_url[1:].replace("-", "_").replace("/", "_")
        return format(random.getrandbits(128), "x")
    except Exception:
        return action_url


def format_date_range(daterange: list[datetime.date]) -> str:
    """
    Prepare string for date range picker field with following format:
    %d/%m/%Y - %d/%m/%Y
    """
    try:
        return f"{daterange[0].strftime('%d/%m/%Y')} - {daterange[1].strftime('%d/%m/%Y')}"
    except Exception:
        return ""


def format_gtl_id(gtl_id: str) -> str:
    return gtl_id.zfill(8)


def format_gtl_as_csr(gtl_id: str) -> Csr | None:
    return get_csr(gtl_id)


def format_finance_incident_status(incident_status: finance_models.IncidentStatus) -> str:
    match incident_status:
        case finance_models.IncidentStatus.CREATED:
            return "Créé"
        case finance_models.IncidentStatus.CANCELLED:
            return "Annulé"
        case finance_models.IncidentStatus.VALIDATED:
            return "Validé"
        case finance_models.IncidentStatus.INVOICED:
            return "Terminé"
        case _:
            return incident_status.value


def format_finance_incident_nature_badge(is_partial: bool) -> str:
    if is_partial:
        return format_badge("Partiel", "info")
    return format_badge("Total", "secondary")


def format_finance_incident_status_badge(incident_status: finance_models.IncidentStatus) -> str:
    match incident_status:
        case finance_models.IncidentStatus.CREATED:
            return format_badge("Créé", "secondary")
        case finance_models.IncidentStatus.CANCELLED:
            return format_badge("Annulé", "danger")
        case finance_models.IncidentStatus.VALIDATED:
            return format_badge("Validé", "success")
        case finance_models.IncidentStatus.INVOICED:
            return format_badge("Terminé", "secondary")


def format_finance_incident_type_str(incident_kind: finance_models.IncidentType) -> str:
    match incident_kind:
        case finance_models.IncidentType.OVERPAYMENT:
            return "Trop Perçu"
        case finance_models.IncidentType.FRAUD:
            return "Fraude"
        case finance_models.IncidentType.COMMERCIAL_GESTURE:
            return "Geste Commercial"
        case finance_models.IncidentType.OFFER_PRICE_REGULATION:
            return "Régulation du prix de l'offre"
        case _:
            return incident_kind.value


def format_finance_incident_type(incident_kind: finance_models.IncidentType) -> str:
    kind_str = format_finance_incident_type_str(incident_kind)
    match incident_kind:
        case finance_models.IncidentType.OVERPAYMENT:
            return format_badge(kind_str, "warning")
        case finance_models.IncidentType.FRAUD:
            return format_badge(kind_str, "danger")
        case finance_models.IncidentType.COMMERCIAL_GESTURE:
            return format_badge(kind_str, "success")
        case finance_models.IncidentType.OFFER_PRICE_REGULATION:
            return format_badge(kind_str, "secondary")
        case _:
            return incident_kind.value


def format_ministry(ministry: str | None) -> str:
    if ministry:
        try:
            return educational_models.Ministry[ministry].value
        except KeyError:
            return ministry
    return ""


def format_notice_type(notice_type: offerers_models.NoticeType) -> str:
    match notice_type:
        case offerers_models.NoticeType.UNPAID_AMOUNT_NOTICE:
            return "Avis de sommes à payer"
        case offerers_models.NoticeType.REMINDER_LETTER:
            return "Lettre de relance"
        case offerers_models.NoticeType.BAILIFF:
            return "Huissier de justice"
        case _:
            return notice_type.value


def format_notice_status_motivation(notice_motivation_type: offerers_models.NoticeStatusMotivation | None) -> str:
    match notice_motivation_type:
        case offerers_models.NoticeStatusMotivation.ALREADY_PAID:
            return "Déjà payé"
        case offerers_models.NoticeStatusMotivation.REJECTED:
            return "Paiement rejeté"
        case offerers_models.NoticeStatusMotivation.NO_LINKED_BANK_ACCOUNT:
            return "Pas de compte bancaire rattaché"
        case offerers_models.NoticeStatusMotivation.OFFERER_NOT_FOUND:
            return "Acteur culturel introuvable"
        case offerers_models.NoticeStatusMotivation.PRICE_NOT_FOUND:
            return "Tarif introuvable"
        case None:
            return ""
        case _:
            return notice_motivation_type.value


def format_notice_status(notice_status: offerers_models.NoticeStatus) -> str:
    match notice_status:
        case offerers_models.NoticeStatus.CREATED:
            return "Nouveau"
        case offerers_models.NoticeStatus.PENDING:
            return "En attente de retour"
        case offerers_models.NoticeStatus.WITHOUT_CONTINUATION:
            return "Classé sans suite"
        case offerers_models.NoticeStatus.CLOSED:
            return "Terminé"
        case _:
            return notice_status.value


def format_special_event_response_status_str(response_status: operations_models.SpecialEventResponseStatus) -> str:
    match response_status:
        case operations_models.SpecialEventResponseStatus.NEW:
            return "Nouvelle"
        case operations_models.SpecialEventResponseStatus.WAITING:
            return "En attente"
        case operations_models.SpecialEventResponseStatus.PRESELECTED:
            return "À contacter"
        case operations_models.SpecialEventResponseStatus.VALIDATED:
            return "Confirmée"
        case operations_models.SpecialEventResponseStatus.REJECTED:
            return "Rejetée"
        case operations_models.SpecialEventResponseStatus.WITHDRAWN:
            return "Désistée"
        case operations_models.SpecialEventResponseStatus.BACKUP:
            return "Backup"
        case _:
            return response_status.value


def format_special_event_response_status(response_status: operations_models.SpecialEventResponseStatus) -> str:
    response_status_str = format_special_event_response_status_str(response_status)
    match response_status:
        case operations_models.SpecialEventResponseStatus.NEW:
            return format_badge(response_status_str, "secondary", "stars")
        case operations_models.SpecialEventResponseStatus.WAITING:
            return format_badge(response_status_str, "warning", "hourglass-split")
        case operations_models.SpecialEventResponseStatus.PRESELECTED:
            return format_badge(response_status_str, "info", "pin-angle-fill")
        case operations_models.SpecialEventResponseStatus.VALIDATED:
            return format_badge(response_status_str, "success", "check2")
        case operations_models.SpecialEventResponseStatus.REJECTED:
            return format_badge(response_status_str, "danger", "x-lg")
        case operations_models.SpecialEventResponseStatus.WITHDRAWN:
            return format_badge(response_status_str, "danger", "ban")
        case operations_models.SpecialEventResponseStatus.BACKUP:
            return format_badge(response_status_str, "primary", "recycle")
        case _:
            return response_status_str


def field_list_get_number_from_name(field_name: str) -> str:
    return field_name.split("-")[1]


def format_collective_location_type(location_type: educational_models.CollectiveLocationType) -> str:
    match location_type:
        case educational_models.CollectiveLocationType.SCHOOL:
            return "Dans l’établissement scolaire"
        case educational_models.CollectiveLocationType.ADDRESS:
            return "À l’adresse"
        case educational_models.CollectiveLocationType.TO_BE_DEFINED:
            return "À déterminer"


def format_legal_category_code(code: int | str) -> str:
    return offerers_constants.CODE_TO_CATEGORY_MAPPING.get(int(code), "Inconnu")


def format_venue_provider_count(count: dict | None) -> str:
    actives = count.get("active", 0) if count else 0
    inactives = count.get("inactive", 0) if count else 0
    return f"{actives} actif{'s' if actives > 1 else ''} / {inactives} inactif{'s' if inactives > 1 else ''}"


def build_pro_link(path: str) -> str:
    if not path.startswith("/"):
        raise ValueError("PRO link path must start with '/'")
    return settings.PRO_URL + path


def get_offer_type(
    offer: offers_models.Offer | educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate,
) -> str:
    if isinstance(offer, educational_models.CollectiveOffer):
        return "collective_offer"
    if isinstance(offer, educational_models.CollectiveOfferTemplate):
        return "collective_offer_template"
    return "offer"


def nl2br(text: str) -> str:
    return escape(text).replace("\n", Markup("<br>"))


def format_chronicle_club_type(club_type: chronicles_models.ChronicleClubType) -> str:
    match club_type:
        case chronicles_models.ChronicleClubType.BOOK_CLUB:
            return "Livres"
        case chronicles_models.ChronicleClubType.CINE_CLUB:
            return "Cinéma"
        case chronicles_models.ChronicleClubType.ALBUM_CLUB:
            return "Musique - albums"
        case chronicles_models.ChronicleClubType.CONCERT_CLUB:
            return "Musique - concerts"
        case _:
            return club_type.value


def format_chronicle_product_identifier_type(chronicle_type: chronicles_models.ChronicleProductIdentifierType) -> str:
    match chronicle_type:
        case chronicles_models.ChronicleProductIdentifierType.ALLOCINE_ID:
            return "ID Allociné"
        case chronicles_models.ChronicleProductIdentifierType.EAN:
            return "EAN"
        case chronicles_models.ChronicleProductIdentifierType.VISA:
            return "Visa"
        case chronicles_models.ChronicleProductIdentifierType.OFFER_ID:
            return "ID de l'offre"
        case _:
            return chronicle_type.value


_SUBSCRIPTION_STATUS_TO_ICON = {
    subscription_schemas.SubscriptionItemStatus.KO.value: "x-circle",
    subscription_schemas.SubscriptionItemStatus.NOT_APPLICABLE.value: "x-circle",
    subscription_schemas.SubscriptionItemStatus.NOT_ENABLED.value: "x-circle",
    subscription_schemas.SubscriptionItemStatus.OK.value: "check-circle",
    subscription_schemas.SubscriptionItemStatus.PENDING.value: "clock",
    subscription_schemas.SubscriptionItemStatus.SKIPPED.value: "exclamation-circle",
    subscription_schemas.SubscriptionItemStatus.SUSPICIOUS.value: "exclamation-circle",
    subscription_schemas.SubscriptionItemStatus.TODO.value: None,
    subscription_schemas.SubscriptionItemStatus.VOID.value: None,
}


def format_user_subscription_tunnel_step_status(status: str) -> str:
    icon = _SUBSCRIPTION_STATUS_TO_ICON.get(status, "exclamation-circle")
    if not icon:
        return ""
    return Markup('<i class="bi bi-{icon}" title="{status}"></i>').format(icon=icon, status=status)


def offer_mediation_link(mediation_id: int, thumb_count: int) -> str | None:
    mediation = offers_models.Mediation(
        id=mediation_id,
        thumbCount=thumb_count,
    )
    return mediation.thumbUrl


def product_mediation_link(uuid: str) -> str | None:
    mediation = offers_models.ProductMediation(
        uuid=uuid,
        imageType=offers_models.ImageType.RECTO,
        productId=0,
    )
    return mediation.url


def format_last_validation_action_name(status: offer_mixin.OfferValidationStatus, prefix: str = "Date") -> str:
    match status:
        case offer_mixin.OfferValidationStatus.APPROVED:
            return f"{prefix} de la dernière validation"
        case offer_mixin.OfferValidationStatus.DRAFT:
            return f"{prefix} de la derniere mise en brouillon"
        case offer_mixin.OfferValidationStatus.PENDING:
            return f"{prefix} de la dernière annulation de validation"
        case offer_mixin.OfferValidationStatus.REJECTED:
            return f"{prefix} du dernier rejet"
        case _:
            return status.value


def install_template_filters(app: Flask) -> None:
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.filters["any"] = any
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
    app.jinja_env.filters["format_action_type"] = format_action_type
    app.jinja_env.filters["format_amount"] = format_amount
    app.jinja_env.filters["format_count"] = format_count
    app.jinja_env.filters["format_badge"] = format_badge
    app.jinja_env.filters["format_booking_cancellation"] = format_booking_cancellation
    app.jinja_env.filters["format_booking_status"] = format_booking_status
    app.jinja_env.filters["format_booking_status_long"] = format_booking_status_long
    app.jinja_env.filters["format_booking_validation_author_type"] = format_booking_validation_author_type
    app.jinja_env.filters["format_bool"] = format_bool
    app.jinja_env.filters["format_bool_badge"] = format_bool_badge
    app.jinja_env.filters["format_cents"] = format_cents
    app.jinja_env.filters["format_rate"] = format_rate
    app.jinja_env.filters["format_rate_multiply_by_100"] = format_rate_multiply_by_100
    app.jinja_env.filters["format_string_list"] = format_string_list
    app.jinja_env.filters["pluralize"] = pluralize
    app.jinja_env.filters["genderize"] = genderize
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_date_time"] = format_date_time
    app.jinja_env.filters["format_string_to_date_time"] = format_string_to_date_time
    app.jinja_env.filters["format_cutoff_date"] = format_cutoff_date
    app.jinja_env.filters["format_timespan"] = format_timespan
    app.jinja_env.filters["format_datespan"] = format_datespan
    app.jinja_env.filters["format_timezone"] = format_timezone
    app.jinja_env.filters["format_deposit_used"] = format_deposit_used
    app.jinja_env.filters["format_active_deposit"] = format_active_deposit
    app.jinja_env.filters["format_validation_status"] = format_validation_status
    app.jinja_env.filters["format_withdrawal_type"] = format_withdrawal_type
    app.jinja_env.filters["format_offer_validation_status"] = format_offer_validation_status
    app.jinja_env.filters["format_offer_status"] = format_offer_status
    app.jinja_env.filters["format_collective_offer_displayed_status"] = format_collective_offer_displayed_status
    app.jinja_env.filters["format_offer_category"] = format_offer_category
    app.jinja_env.filters["format_offer_subcategory"] = format_offer_subcategory
    app.jinja_env.filters["format_offerer_rejection_reason"] = format_offerer_rejection_reason
    app.jinja_env.filters["format_offerer_status_badge"] = format_offerer_status_badge
    app.jinja_env.filters["format_collective_offer_formats"] = format_collective_offer_formats
    app.jinja_env.filters["format_subcategories"] = format_subcategories
    app.jinja_env.filters["format_collective_offer_rejection_reason"] = format_collective_offer_rejection_reason
    app.jinja_env.filters["format_product_cgu_compatibility_status"] = format_product_cgu_compatibility_status
    app.jinja_env.filters["format_as_badges"] = format_as_badges
    app.jinja_env.filters["format_compliance_reasons"] = format_compliance_reasons
    app.jinja_env.filters["format_offer_compliance_llm_validation"] = format_offer_compliance_llm_validation
    app.jinja_env.filters["format_confidence_level_badge"] = format_confidence_level_badge
    app.jinja_env.filters["format_confidence_level_badge_for_venue"] = format_confidence_level_badge_for_venue
    app.jinja_env.filters["format_criteria"] = format_criteria
    app.jinja_env.filters["format_tag_object_list"] = format_tag_object_list
    app.jinja_env.filters["format_fraud_review_status"] = format_fraud_review_status
    app.jinja_env.filters["format_dms_status"] = format_dms_status
    app.jinja_env.filters["format_dms_application_status"] = format_dms_application_status
    app.jinja_env.filters["format_dms_application_status_badge"] = format_dms_application_status_badge
    app.jinja_env.filters["format_user_account_update_flags"] = format_user_account_update_flags
    app.jinja_env.filters["format_user_account_update_type"] = format_user_account_update_type
    app.jinja_env.filters["format_registration_step_description"] = format_registration_step_description
    app.jinja_env.filters["format_subscription_step"] = format_subscription_step
    app.jinja_env.filters["format_eligibility_value"] = format_eligibility_value
    app.jinja_env.filters["format_eligibility_type"] = format_eligibility_type
    app.jinja_env.filters["format_fraud_check_url"] = format_fraud_check_url
    app.jinja_env.filters["format_fraud_action_dict_url"] = format_fraud_action_dict_url
    app.jinja_env.filters["format_legal_category_code"] = format_legal_category_code
    app.jinja_env.filters["format_role"] = format_role
    app.jinja_env.filters["format_state"] = format_state
    app.jinja_env.filters["format_reason_label"] = format_reason_label
    app.jinja_env.filters["format_modified_info_values"] = format_modified_info_values
    app.jinja_env.filters["format_modified_info_name"] = format_modified_info_name
    app.jinja_env.filters["format_permission_name"] = format_permission_name
    app.jinja_env.filters["format_gtl_id"] = format_gtl_id
    app.jinja_env.filters["format_gtl_as_csr"] = format_gtl_as_csr
    app.jinja_env.filters["format_offer_validation_rule_list"] = format_offer_validation_rule_list
    app.jinja_env.filters["format_sub_rules_info_type"] = format_sub_rules_info_type
    app.jinja_env.filters["format_offer_validation_sub_rule"] = format_offer_validation_sub_rule
    app.jinja_env.filters["format_offer_validation_operator"] = format_offer_validation_operator
    app.jinja_env.filters["format_music_gtl_id"] = format_music_gtl_id
    app.jinja_env.filters["format_show_type"] = format_show_type
    app.jinja_env.filters["format_show_subtype"] = format_show_subtype
    app.jinja_env.filters["format_user_offerer_status_badge"] = format_user_offerer_status_badge
    app.jinja_env.filters["get_comparated_format_function"] = get_comparated_format_function
    app.jinja_env.filters["format_offer_types"] = format_offer_types
    app.jinja_env.filters["format_website"] = format_website
    app.jinja_env.filters["format_venue_target"] = format_venue_target
    app.jinja_env.filters["format_pivot_name"] = format_pivot_name
    app.jinja_env.filters["format_titelive_id_lectorat"] = format_titelive_id_lectorat
    app.jinja_env.filters["format_date_range"] = format_date_range
    app.jinja_env.filters["parse_referrer"] = parse_referrer
    app.jinja_env.filters["unescape"] = html.unescape
    app.jinja_env.filters["action_to_name"] = action_to_name
    app.jinja_env.filters["field_list_get_number_from_name"] = field_list_get_number_from_name
    app.jinja_env.filters["pc_pro_offer_link"] = urls.build_pc_pro_offer_path
    app.jinja_env.filters["pc_backoffice_public_account_link"] = urls.build_backoffice_public_account_link
    app.jinja_env.filters["pc_backoffice_public_account_link_in_comment"] = (
        urls.build_backoffice_public_account_link_in_comment
    )
    app.jinja_env.filters["webapp_offer_link"] = lambda offer: urls.offer_app_link(offer.id)
    app.jinja_env.filters["webapp_venue_link"] = lambda venue: urls.venue_app_link(venue.id)
    app.jinja_env.filters["format_gdpr_date_processed"] = format_gdpr_date_processed
    app.jinja_env.filters["format_finance_incident_nature_badge"] = format_finance_incident_nature_badge
    app.jinja_env.filters["format_finance_incident_status_badge"] = format_finance_incident_status_badge
    app.jinja_env.filters["format_finance_incident_type"] = format_finance_incident_type
    app.jinja_env.filters["format_finance_incident_type_str"] = format_finance_incident_type_str
    app.jinja_env.filters["format_ministry"] = format_ministry
    app.jinja_env.filters["format_notice_type"] = format_notice_type
    app.jinja_env.filters["format_notice_status_motivation"] = format_notice_status_motivation
    app.jinja_env.filters["format_notice_status"] = format_notice_status
    app.jinja_env.filters["format_special_event_response_status"] = format_special_event_response_status
    app.jinja_env.filters["format_venue_provider_count"] = format_venue_provider_count
    app.jinja_env.filters["format_last_validation_action_name"] = format_last_validation_action_name
    app.jinja_env.filters["build_pro_link"] = build_pro_link
    app.jinja_env.filters["offer_type"] = get_offer_type
    app.jinja_env.filters["nl2br"] = nl2br
    app.jinja_env.filters["format_user_subscription_tunnel_step_status"] = format_user_subscription_tunnel_step_status
    app.jinja_env.filters["offer_mediation_link"] = offer_mediation_link
    app.jinja_env.filters["product_mediation_link"] = product_mediation_link
    app.jinja_env.filters["format_artist_visibility_status"] = format_artist_visibility_status
    app.jinja_env.filters["format_collective_location_type"] = format_collective_location_type
    app.jinja_env.filters["format_chronicle_product_identifier_type"] = format_chronicle_product_identifier_type
    app.jinja_env.filters["get_chronicle_product_identifier"] = chronicles_api.get_product_identifier
    app.jinja_env.filters["format_user_profile_refresh_campaign_action_type"] = (
        format_user_profile_refresh_campaign_action_type
    )
