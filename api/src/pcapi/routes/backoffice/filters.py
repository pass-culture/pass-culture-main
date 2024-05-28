import datetime
import decimal
import html
import logging
import random
import re
import typing
from urllib.parse import urlparse
from urllib.parse import urlunparse

from flask import Flask
from markupsafe import Markup
import psycopg2.extras
import pytz

from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.bookings import models as bookings_models
from pcapi.core.categories import categories
from pcapi.core.categories import subcategories_v2
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import api as finance_api
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offerers import constants as offerers_constants
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.domain import music_types
from pcapi.domain import show_types
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.routes.backoffice.accounts import serialization as serialization_accounts
from pcapi.utils import urls
from pcapi.utils.csr import Csr
from pcapi.utils.csr import get_csr


logger = logging.getLogger(__name__)

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
        case users_models.UserRole.PRO | users_models.UserRole.NON_ATTACHED_PRO:
            return "Pro"
        case users_models.UserRole.TEST:
            return "Test"
        case users_models.UserRole.BENEFICIARY:
            return "Pass 18"
        case users_models.UserRole.UNDERAGE_BENEFICIARY:
            return "Pass 15-17"
        case _:
            return "Aucune information"


def format_deposit_type(deposit_type: finance_models.DepositType) -> str:
    match deposit_type:
        case finance_models.DepositType.GRANT_18:
            return "<span class='badge text-bg-secondary'>Pass 18</span>"
        case finance_models.DepositType.GRANT_15_17:
            return "<span class='badge text-bg-secondary'>Pass 15-17</span>"
        case _:
            return "Aucune information"


def format_active_deposit(deposit: finance_models.Deposit | None) -> str:
    if deposit:
        if not deposit.expirationDate or deposit.expirationDate > datetime.datetime.utcnow():
            return Markup('<span class="visually-hidden">Oui</span><i class="bi bi-check-circle-fill"></i>')
    return Markup('<span class="visually-hidden">Non</span><i class="bi bi-x-circle-fill"></i>')


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


def format_date_time(data: datetime.date | datetime.datetime) -> str:
    return format_date(data, strformat="%d/%m/%Y à %Hh%M")


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


def format_amount(amount: float | decimal.Decimal | None) -> str:
    if amount is None:
        amount = 0.0

    return Markup('<span class="text-nowrap">{formatted_amount} €</span>').format(
        formatted_amount=f"{amount:,.2f}".replace(",", "\u202f").replace(".", ",")
    )


def format_cents(amount_in_cents: int | None) -> str:
    if amount_in_cents is None:
        amount_in_cents = 0

    return format_amount(finance_utils.to_euros(amount_in_cents))


def format_rate(rate: float | None) -> str:
    if rate is None:
        return "N/A"

    return f"{rate}\u202f%".replace(".", ",")


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
        return Markup(
            '<span class="mx-2 pb-1 badge rounded-pill text-bg-success"><i class="bi bi-check-circle"></i> Oui</span>'
        )
    return Markup('<span class="mx-2 pb-1 badge rounded-pill text-bg-dark"><i class="bi bi-x-circle"></i> Non</span>')


def format_string_list(data: list[str] | None) -> str:
    if data is None:
        return ""
    return ", ".join(data)


def pluralize(count: int, singular: str = "", plural: str = "s") -> str:
    return plural if count > 1 else singular


def format_reason_label(reason: str | None) -> str:
    if reason:
        return users_constants.SUSPENSION_REASON_CHOICES.get(
            users_constants.SuspensionReason(reason), "Raison inconnue"
        )
    return ""


def format_booking_cancellation_reason(
    reason: bookings_models.BookingCancellationReasons | educational_models.CollectiveBookingCancellationReasons | None,
) -> str:
    match reason:
        case (
            bookings_models.BookingCancellationReasons.OFFERER
            | educational_models.CollectiveBookingCancellationReasons.OFFERER
        ):
            return "Annulée par l'acteur culturel"
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
            return "Fraude"
        case (
            educational_models.CollectiveBookingCancellationReasons.FINANCE_INCIDENT
            | bookings_models.BookingCancellationReasons.FINANCE_INCIDENT
        ):
            return "Incident finance"
        case (
            educational_models.CollectiveBookingCancellationReasons.BACKOFFICE
            | bookings_models.BookingCancellationReasons.BACKOFFICE
        ):
            return "Annulée sur le backoffice"
        case (
            bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
            | educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        ):
            return "Refusée par l'institution"
        case educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER:
            return "Refusée par le chef d'établissement"
        case None:
            return ""
        case _:
            return reason.value


def format_booking_status_long(booking: bookings_models.Booking | educational_models.CollectiveBooking) -> str:
    if booking.status in (
        bookings_models.BookingStatus.REIMBURSED,
        educational_models.CollectiveBookingStatus.REIMBURSED,
    ):
        return '<span class="badge text-bg-success">AC remboursé</span>'
    if booking.status in (
        bookings_models.BookingStatus.CANCELLED,
        educational_models.CollectiveBookingStatus.CANCELLED,
    ):
        return "<span class=\"badge text-bg-danger\">L'offre n'a pas eu lieu</span>"
    if booking.status in (bookings_models.BookingStatus.USED, educational_models.CollectiveBookingStatus.USED):
        return '<span class="badge text-bg-success">Le jeune a consommé l\'offre</span>'
    if isinstance(booking, bookings_models.Booking) and booking.isConfirmed:
        return '<span class="badge text-bg-success">Le jeune ne peut plus annuler</span>'
    if (
        isinstance(booking, educational_models.CollectiveBooking)
        and booking.status == educational_models.CollectiveBookingStatus.CONFIRMED
    ):
        return '<span class="badge text-bg-success">Le chef d\'établissement a validé la réservation</span>'
    if booking.status == educational_models.CollectiveBookingStatus.PENDING:
        return '<span class="badge text-bg-success">L\'enseignant a posé une option</span>'
    return '<span class="badge text-bg-success">Le jeune a réservé l\'offre</span>'


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
        return '<span class="badge text-bg-success">Remboursée</span>' if with_badge else "Remboursée"
    if booking.status in (
        bookings_models.BookingStatus.CANCELLED,
        educational_models.CollectiveBookingStatus.CANCELLED,
    ):
        return '<span class="badge text-bg-danger">Annulée</span>' if with_badge else "Annulée"
    if booking.status in (bookings_models.BookingStatus.USED, educational_models.CollectiveBookingStatus.USED):
        return '<span class="badge text-bg-success">Validée</span>' if with_badge else "Validée"
    if isinstance(booking, bookings_models.Booking) and booking.isConfirmed:
        return "Confirmée"
    if (
        isinstance(booking, educational_models.CollectiveBooking)
        and booking.status == educational_models.CollectiveBookingStatus.CONFIRMED
    ):
        return "Confirmée"
    if booking.status == educational_models.CollectiveBookingStatus.PENDING:
        return '<span class="text-nowrap">Pré-réservée</span>' if with_badge else "Pré-réservée"
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
        case _:
            return status.value


def format_offer_validation_status(status: offer_mixin.OfferValidationStatus) -> str:
    match status:
        case offer_mixin.OfferValidationStatus.DRAFT:
            return "Nouvelle"
        case offer_mixin.OfferValidationStatus.PENDING:
            return "En attente"
        case offer_mixin.OfferValidationStatus.APPROVED:
            return "Validée"
        case offer_mixin.OfferValidationStatus.REJECTED:
            return "Rejetée"
        case _:
            return status.value


def format_offer_status(status: offer_mixin.OfferStatus) -> str:
    match status:
        case offer_mixin.OfferStatus.DRAFT:
            return "Brouillon"
        case offer_mixin.OfferStatus.ACTIVE:
            return "Active"
        case offer_mixin.OfferStatus.PENDING:
            return "Pré-réservée"
        case offer_mixin.OfferStatus.EXPIRED:
            return "Expirée"
        case offer_mixin.OfferStatus.REJECTED:
            return "Rejetée"
        case offer_mixin.OfferStatus.SOLD_OUT:
            return "Épuisée"
        case offer_mixin.OfferStatus.INACTIVE:
            return "Inactive"
        case _:
            return status.value


def format_offer_category(subcategory_id: str) -> str:
    subcategory = subcategories_v2.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if subcategory:
        return subcategory.category.pro_label
    return ""


def format_offer_subcategory(subcategory_id: str) -> str:
    subcategory = subcategories_v2.ALL_SUBCATEGORIES_DICT.get(subcategory_id)
    if subcategory:
        return subcategory.pro_label
    return ""


def format_collective_offer_formats(formats: typing.Sequence[subcategories_v2.EacFormat] | None) -> str:
    if not formats:
        return ""
    try:
        return ", ".join([fmt.value for fmt in formats])
    except Exception:  # pylint: disable=broad-exception-caught
        return "<inconnus>"


def format_subcategories(subcategories: list[str]) -> str:
    if subcategories == []:
        return ""
    labels = sorted(
        subcategories_v2.ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label for subcategory_id in subcategories
    )
    displayed_labels = ", ".join(labels)
    return displayed_labels


def format_fraud_review_status(status: fraud_models.FraudReviewStatus) -> str:
    match status:
        case fraud_models.FraudReviewStatus.OK:
            return "OK"
        case fraud_models.FraudReviewStatus.KO:
            return "KO"
        case fraud_models.FraudReviewStatus.REDIRECTED_TO_DMS:
            return "Redirigé vers DMS"
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
        case _:
            return status.value


def format_registration_step_description(description: str) -> str:
    description = format_subscription_step(description)
    description = format_eligibility_value(description)
    return description


def format_subscription_step(step_value: str) -> str:
    match step_value.lower():
        case "email-validation":
            return "Validation Email"
        case "phone-validation":
            return "Validation N° téléphone"
        case "profile-completion":
            return "Profil Complet"
        case "identity-check":
            return "ID Check"
        case "honor-statement":
            return "Attestation sur l'honneur"
        case _:
            return step_value


def format_eligibility_value(tunnel_type: str) -> str:
    match tunnel_type.lower():
        case "underage":
            return "Pass 15-17"
        case "age-18":
            return "Pass 18"
        case "underage+age-18":
            return "Pass 15-17+18"
        case "not-eligible":
            return "Non éligible"
        case _:
            return tunnel_type


def format_eligibility_type(eligibility_type: users_models.EligibilityType) -> str:
    match eligibility_type:
        case users_models.EligibilityType.UNDERAGE:
            return "Pass 15-17"
        case users_models.EligibilityType.AGE18:
            return "Pass 18"
        case _:
            return eligibility_type.value


def format_as_badges(items: list[str] | None) -> str:
    if not items:
        return ""

    return " ".join(
        Markup('<span class="badge text-bg-light shadow-sm">{name}</span>').format(name=item) for item in items
    )


def format_tag_object_list(
    objects_with_label_attribute: list[offerers_models.OffererTag] | list[offerers_models.OffererTagCategory],
) -> str:
    if objects_with_label_attribute:
        return format_as_badges(
            [getattr(obj, "label", getattr(obj, "name", "")) for obj in objects_with_label_attribute]
        )
    return ""


def format_criteria(criteria: list[criteria_models.OfferCriterion]) -> str:
    return format_as_badges([criterion.name for criterion in criteria])


def format_compliance_reason(feature: str) -> str:
    match feature:
        case "offer_name":
            return "Nom de l'offre"
        case "offer_description":
            return "Description de l'offre"
        case "offer_subcategoryid":
            return "Sous-catégorie"
        case "rayon":
            return "Rayon"
        case "macro_rayon":
            return "Macro-rayon"
        case "stock_price":
            return "Prix"
        case "thumb_url":
            return "Image de l'offre"
        case "offer_type_label":
            return "Genre musical / type de spectacle"
        case "offer_sub_type_label":
            return "Sous-genre"
        case "author":
            return "Auteur"
        case "performer":
            return "Interprète"
        case _:
            return feature


def format_compliance_reasons(features: list[str]) -> str:
    return format_as_badges([format_compliance_reason(feature) for feature in features])


def format_confidence_level(confidence_level: offerers_models.OffererConfidenceLevel | None) -> str:
    match confidence_level:
        case offerers_models.OffererConfidenceLevel.MANUAL_REVIEW:
            return "Revue manuelle de toutes les offres"
        case offerers_models.OffererConfidenceLevel.WHITELIST:
            return "Validation automatique (liste blanche)"
        case None:
            return "Suivre les règles"

    return confidence_level


def format_confidence_level_badge(
    confidence_level: offerers_models.OffererConfidenceLevel, show_no_rule: bool = False, info: str = ""
) -> str:
    match confidence_level:
        case offerers_models.OffererConfidenceLevel.MANUAL_REVIEW:
            return Markup('<span class="badge text-bg-danger shadow-sm">Revue manuelle {info}</span>').format(info=info)
        case offerers_models.OffererConfidenceLevel.WHITELIST:
            return Markup('<span class="badge text-bg-success shadow-sm">Validation auto {info}</span>').format(
                info=info
            )

    if show_no_rule:
        return Markup('<span class="badge text-bg-light shadow-sm">Suivre les règles</span>')

    return ""


def format_confidence_level_badge_for_venue(venue: offerers_models.Venue) -> str:
    if venue.confidenceLevel:
        return format_confidence_level_badge(venue.confidenceLevel)

    return format_confidence_level_badge(venue.managingOfferer.confidenceLevel, show_no_rule=True, info="(structure)")


def format_fraud_check_url(id_check_item: serialization_accounts.IdCheckItemModel) -> str:
    if id_check_item.type == fraud_models.FraudCheckType.UBBLE.value:
        return f"https://dashboard.ubble.ai/identifications/{id_check_item.thirdPartyId}"
    if id_check_item.type == fraud_models.FraudCheckType.DMS.value and id_check_item.technicalDetails:
        return f"https://www.demarches-simplifiees.fr/procedures/{id_check_item.technicalDetails['procedure_number']}/dossiers/{id_check_item.thirdPartyId}"
    return ""


def format_fraud_action_dict_url(fraud_action_dict: dict) -> str:
    if fraud_action_dict["type"] == fraud_models.FraudCheckType.UBBLE.value:
        return f"https://dashboard.ubble.ai/identifications/{fraud_action_dict['techId']}"
    if fraud_action_dict["type"] == fraud_models.FraudCheckType.DMS.value and fraud_action_dict["technicalDetails"]:
        return f"https://www.demarches-simplifiees.fr/procedures/{fraud_action_dict['technicalDetails']['procedure_number']}/dossiers/{fraud_action_dict['techId']}"
    return ""


def _format_modified_info_value(value: typing.Any, name: str | None = None) -> str:
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
    return str(value)


def format_modified_info_values(modified_info: typing.Any, name: str | None = None) -> str:
    old_info = modified_info.get("old_info")
    new_info = modified_info.get("new_info")

    if old_info is not None and new_info is not None:
        return Markup("{old_value} => {new_value}").format(
            old_value=_format_modified_info_value(old_info, name),
            new_value=_format_modified_info_value(new_info, name),
        )

    if old_info is not None:
        return Markup("suppression de : {value}").format(value=_format_modified_info_value(old_info, name))

    if new_info is not None:
        return Markup("ajout de : {value}").format(value=_format_modified_info_value(new_info, name))

    return str(modified_info)  # this should not happen if data is consistent


def format_music_type(music_type_id: int | str) -> str:
    try:
        return music_types.MUSIC_TYPES_LABEL_BY_CODE.get(int(music_type_id), f"Autre[{music_type_id}]")
    except ValueError:
        return f"Autre[{music_type_id}]"


def format_music_subtype(music_subtype_id: int | str) -> str:
    try:
        return music_types.MUSIC_SUB_TYPES_LABEL_BY_CODE.get(int(music_subtype_id), f"Autre[{music_subtype_id}]")
    except ValueError:
        return f"Autre[{music_subtype_id}]"


def format_show_type(show_type_id: int | str) -> str:
    try:
        return show_types.SHOW_TYPES_LABEL_BY_CODE.get(int(show_type_id), f"Autre[{show_type_id}]")
    except ValueError:
        return f"Autre[{show_type_id}]"


def format_show_subtype(show_subtype_id: int | str) -> str:
    try:
        return show_types.SHOW_SUB_TYPES_LABEL_BY_CODE.get(int(show_subtype_id), f"Autre[{show_subtype_id}]")
    except ValueError:
        return f"Autre[{show_subtype_id}]"


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
        case "pro_new_nav_state.newNavDate":
            return "Date de passage sur la nouvelle interface Pro"
        case "pro_new_nav_state.eligibilityDate":
            return "Date d'éligibilité à la nouvelle interface Pro"
        case "confidenceRule.confidenceLevel":
            return "Validation des offres"

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
            return "Le lieu proposant l'offre"
        case offers_models.OfferValidationSubRuleField.ID_OFFERER:
            return "La structure proposant l'offre"
        case offers_models.OfferValidationSubRuleField.FORMATS_COLLECTIVE_OFFER:
            return "Les formats de l'offre collective"
        case offers_models.OfferValidationSubRuleField.FORMATS_COLLECTIVE_OFFER_TEMPLATE:
            return "Les formats de l'offre collective vitrine"
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
            return lambda category_id: categories.ALL_CATEGORIES_DICT[category_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SUBCATEGORY_ID:
            return lambda subcategory_id: subcategories_v2.ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SHOW_SUB_TYPE:
            return lambda show_sub_type_code: show_types.SHOW_SUB_TYPES_LABEL_BY_CODE[int(show_sub_type_code)]
        if sub_rule.attribute == offers_models.OfferValidationAttribute.FORMATS:
            return lambda fmt: subcategories_v2.EacFormat[fmt].value
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
    except Exception:  # pylint: disable=broad-except
        return "/"


def action_to_name(action_url: str) -> str:
    """
    Slugify a form action path to a name so form can be controlled with JS.
    """
    try:
        if len(action_url) != 0:
            return action_url[1:].replace("-", "_").replace("/", "_")
        return format(random.getrandbits(128), "x")
    except Exception:  # pylint: disable=broad-except
        return action_url


def format_date_range(daterange: list[datetime.date]) -> str:
    """
    Prepare string for date range picker field with following format:
    %d/%m/%Y - %d/%m/%Y
    """
    try:
        return f"{daterange[0].strftime('%d/%m/%Y')} - {daterange[1].strftime('%d/%m/%Y')}"
    except Exception:  # pylint: disable=broad-except
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
        case _:
            return incident_status.value


def format_finance_incident_nature_badge(is_partial: bool) -> str:
    if is_partial:
        return Markup('<span class="badge text-bg-info">Partiel</span>')
    return Markup('<span class="badge text-bg-secondary">Total</span>')


def format_finance_incident_status_badge(incident_status: finance_models.IncidentStatus) -> str:
    match incident_status:
        case finance_models.IncidentStatus.CREATED:
            return Markup('<span class="badge text-bg-secondary">Créé</span>')
        case finance_models.IncidentStatus.CANCELLED:
            return Markup('<span class="badge text-bg-danger">Annulé</span>')
        case finance_models.IncidentStatus.VALIDATED:
            return Markup('<span class="badge text-bg-success">Validé</span>')


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
            return Markup('<span class="badge text-bg-warning">{kind}</span>').format(kind=kind_str)
        case finance_models.IncidentType.FRAUD:
            return Markup('<span class="badge text-bg-danger">{kind}</span>').format(kind=kind_str)
        case finance_models.IncidentType.COMMERCIAL_GESTURE:
            return Markup('<span class="badge text-bg-success">{kind}</span>').format(kind=kind_str)
        case finance_models.IncidentType.OFFER_PRICE_REGULATION:
            return Markup('<span class="badge text-bg-light">{kind}</span>').format(kind=kind_str)
        case _:
            return incident_kind.value


def field_list_get_number_from_name(field_name: str) -> str:
    return field_name.split("-")[1]


def format_legal_category_code(code: int | str) -> str:
    return offerers_constants.CODE_TO_CATEGORY_MAPPING.get(int(code), "Inconnu")


def install_template_filters(app: Flask) -> None:
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
    app.jinja_env.filters["format_amount"] = format_amount
    app.jinja_env.filters["format_booking_cancellation_reason"] = format_booking_cancellation_reason
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
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_date_time"] = format_date_time
    app.jinja_env.filters["format_string_to_date_time"] = format_string_to_date_time
    app.jinja_env.filters["format_cutoff_date"] = format_cutoff_date
    app.jinja_env.filters["format_timespan"] = format_timespan
    app.jinja_env.filters["format_deposit_type"] = format_deposit_type
    app.jinja_env.filters["format_active_deposit"] = format_active_deposit
    app.jinja_env.filters["format_validation_status"] = format_validation_status
    app.jinja_env.filters["format_offer_validation_status"] = format_offer_validation_status
    app.jinja_env.filters["format_offer_status"] = format_offer_status
    app.jinja_env.filters["format_offer_category"] = format_offer_category
    app.jinja_env.filters["format_offer_subcategory"] = format_offer_subcategory
    app.jinja_env.filters["format_collective_offer_formats"] = format_collective_offer_formats
    app.jinja_env.filters["format_subcategories"] = format_subcategories
    app.jinja_env.filters["format_as_badges"] = format_as_badges
    app.jinja_env.filters["format_compliance_reasons"] = format_compliance_reasons
    app.jinja_env.filters["format_confidence_level_badge"] = format_confidence_level_badge
    app.jinja_env.filters["format_confidence_level_badge_for_venue"] = format_confidence_level_badge_for_venue
    app.jinja_env.filters["format_criteria"] = format_criteria
    app.jinja_env.filters["format_tag_object_list"] = format_tag_object_list
    app.jinja_env.filters["format_fraud_review_status"] = format_fraud_review_status
    app.jinja_env.filters["format_dms_status"] = format_dms_status
    app.jinja_env.filters["format_dms_application_status"] = format_dms_application_status
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
    app.jinja_env.filters["format_music_type"] = format_music_type
    app.jinja_env.filters["format_music_subtype"] = format_music_subtype
    app.jinja_env.filters["format_show_type"] = format_show_type
    app.jinja_env.filters["format_show_subtype"] = format_show_subtype
    app.jinja_env.filters["get_comparated_format_function"] = get_comparated_format_function
    app.jinja_env.filters["format_offer_types"] = format_offer_types
    app.jinja_env.filters["format_website"] = format_website
    app.jinja_env.filters["format_venue_target"] = format_venue_target
    app.jinja_env.filters["format_titelive_id_lectorat"] = format_titelive_id_lectorat
    app.jinja_env.filters["format_date_range"] = format_date_range
    app.jinja_env.filters["parse_referrer"] = parse_referrer
    app.jinja_env.filters["unescape"] = html.unescape
    app.jinja_env.filters["action_to_name"] = action_to_name
    app.jinja_env.filters["field_list_get_number_from_name"] = field_list_get_number_from_name
    app.jinja_env.filters["pc_pro_bank_account_link"] = urls.build_pc_pro_bank_account_link
    app.jinja_env.filters["pc_pro_offer_link"] = urls.build_pc_pro_offer_link
    app.jinja_env.filters["pc_pro_offerer_link"] = urls.build_pc_pro_offerer_link
    app.jinja_env.filters["pc_pro_offerer_offers_link"] = urls.build_pc_pro_offerer_offers_link
    app.jinja_env.filters["pc_pro_venue_bookings_link"] = urls.build_pc_pro_venue_bookings_link
    app.jinja_env.filters["pc_pro_venue_offers_link"] = urls.build_pc_pro_venue_offers_link
    app.jinja_env.filters["pc_pro_venue_link"] = urls.build_pc_pro_venue_link
    app.jinja_env.filters["pc_backoffice_public_account_link"] = urls.build_backoffice_public_account_link
    app.jinja_env.filters["pc_backoffice_public_account_link_in_comment"] = (
        urls.build_backoffice_public_account_link_in_comment
    )
    app.jinja_env.filters["format_finance_incident_nature_badge"] = format_finance_incident_nature_badge
    app.jinja_env.filters["format_finance_incident_status_badge"] = format_finance_incident_status_badge
    app.jinja_env.filters["format_finance_incident_type"] = format_finance_incident_type
    app.jinja_env.filters["format_finance_incident_type_str"] = format_finance_incident_type_str
