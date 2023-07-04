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
from pcapi.core.finance import models as finance_models
from pcapi.core.finance import utils as finance_utils
from pcapi.core.fraud import models as fraud_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models
from pcapi.domain.show_types import SHOW_SUB_TYPES_LABEL_BY_CODE
from pcapi.models import offer_mixin
from pcapi.routes.backoffice_v3.serialization import accounts as serialization_accounts
from pcapi.utils import urls


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

    return f"{amount:,.2f} €".replace(",", "\u202f").replace(".", ",")


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


def format_reason_label(reason: str | None) -> str:
    if reason:
        return users_constants.SUSPENSION_REASON_CHOICES.get(
            users_constants.SuspensionReason(reason), "Raison inconnue"
        )
    return ""


def format_booking_cancellation_reason(
    reason: bookings_models.BookingCancellationReasons | educational_models.CollectiveBookingCancellationReasons,
) -> str:
    match reason:
        case bookings_models.BookingCancellationReasons.OFFERER | educational_models.CollectiveBookingCancellationReasons.OFFERER:
            return "Annulée par l'acteur culturel"
        case bookings_models.BookingCancellationReasons.BENEFICIARY | educational_models.CollectiveBookingCancellationReasons.BENEFICIARY:
            return "Annulée par le bénéficiaire"
        case bookings_models.BookingCancellationReasons.EXPIRED | educational_models.CollectiveBookingCancellationReasons.EXPIRED:
            return "Expirée"
        case bookings_models.BookingCancellationReasons.FRAUD | educational_models.CollectiveBookingCancellationReasons.FRAUD:
            return "Fraude"
        case bookings_models.BookingCancellationReasons.REFUSED_BY_INSTITUTE | educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE:
            return "Refusée par l'institution"
        case educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER:
            return "Refusée par le chef d'établissement"
        case _:
            return ""


def format_booking_status_long(status: bookings_models.BookingStatus) -> str:
    match status:
        case bookings_models.BookingStatus.CONFIRMED:
            return "Réservation confirmée"
        case bookings_models.BookingStatus.USED:
            return '<span class="badge text-bg-success">Le jeune a consommé l\'offre</span>'
        case bookings_models.BookingStatus.CANCELLED:
            return "<span class=\"badge text-bg-danger\">L'offre n'a pas eu lieu</span>"
        case bookings_models.BookingStatus.REIMBURSED:
            return '<span class="badge text-bg-success">AC remboursé</span>'
        case _:
            return status.value


def format_booking_status(
    status: bookings_models.BookingStatus | educational_models.CollectiveBookingStatus, with_badge: bool = False
) -> str:
    match status:
        case educational_models.CollectiveBookingStatus.PENDING:
            return '<span class="text-nowrap">Pré-réservée</span>' if with_badge else "Pré-réservée"
        case bookings_models.BookingStatus.CONFIRMED | educational_models.CollectiveBookingStatus.CONFIRMED:
            return "Confirmée"
        case bookings_models.BookingStatus.USED | educational_models.CollectiveBookingStatus.USED:
            return '<span class="badge text-bg-success">Validée</span>' if with_badge else "Validée"
        case bookings_models.BookingStatus.CANCELLED | educational_models.CollectiveBookingStatus.CANCELLED:
            return '<span class="badge text-bg-danger">Annulée</span>' if with_badge else "Annulée"
        case bookings_models.BookingStatus.REIMBURSED | educational_models.CollectiveBookingStatus.REIMBURSED:
            return '<span class="badge text-bg-success">Remboursée</span>' if with_badge else "Remboursée"
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


def format_subcategories(subcategories: list[str]) -> str:
    if subcategories == []:
        return ""
    labels = sorted(
        subcategories_v2.ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label for subcategory_id in subcategories
    )
    displayed_labels = ", ".join(labels)
    return displayed_labels


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


def format_graphql_application_status(status: GraphQLApplicationStates) -> str:
    match status:
        case GraphQLApplicationStates.accepted:
            return "Accepté"
        case GraphQLApplicationStates.on_going:
            return "En instruction"
        case GraphQLApplicationStates.draft:
            return "En construction"
        case GraphQLApplicationStates.refused:
            return "Refusé"
        case GraphQLApplicationStates.without_continuation:
            return "Classé sans suite"
        case _:
            return status.value


def format_tag_object_list(
    objects_with_label_attribute: list[offerers_models.OffererTag] | list[offerers_models.OffererTagCategory],
) -> str:
    if objects_with_label_attribute:
        return ", ".join([(obj.label or obj.name) for obj in objects_with_label_attribute])
    return ""


def format_criteria(criteria: list[criteria_models.OfferCriterion]) -> str:
    return " ".join(
        Markup('<span class="badge text-bg-light shadow-sm">{name}</span>').format(name=criterion.name)
        for criterion in criteria
    )


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


def format_adage_referred(venues: list[offerers_models.Venue]) -> str:
    return f"{len([venue for venue in venues if venue.adageId])}/{len(venues)}"


def format_modified_info_value(value: typing.Any) -> str:
    if isinstance(value, list):
        return format_string_list(value)
    return str(value)


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
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_OFFER:
            return "La description de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_COLLECTIVE_OFFER:
            return "La description de l'offre collective"
        case offers_models.OfferValidationSubRuleField.DESCRIPTION_COLLECTIVE_OFFER_TEMPLATE:
            return "La description de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.SUBCATEGORY_OFFER:
            return "La sous-catégorie de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.SUBCATEGORY_COLLECTIVE_OFFER:
            return "La sous-catégorie de l'offre collective"
        case offers_models.OfferValidationSubRuleField.SUBCATEGORY_COLLECTIVE_OFFER_TEMPLATE:
            return "La sous-catégorie de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.CATEGORY_OFFER:
            return "La catégorie de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.CATEGORY_COLLECTIVE_OFFER:
            return "La catégorie de l'offre collective"
        case offers_models.OfferValidationSubRuleField.CATEGORY_COLLECTIVE_OFFER_TEMPLATE:
            return "La catégorie de l'offre collective vitrine"
        case offers_models.OfferValidationSubRuleField.SHOW_SUB_TYPE_OFFER:
            return "Le sous-type de spectacle de l'offre individuelle"
        case offers_models.OfferValidationSubRuleField.ID_OFFERER:
            return "La structure proposant l'offre"
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


def get_comparated_format_function(
    sub_rule: offers_models.OfferValidationSubRule,
    offerer_dict: dict,
) -> typing.Callable[[typing.Any], typing.Any]:
    try:
        if (
            sub_rule.attribute == offers_models.OfferValidationAttribute.ID
            and sub_rule.model == offers_models.OfferValidationModel.OFFERER
        ):
            return lambda offerer_id: offerer_dict[offerer_id]
        if sub_rule.attribute == offers_models.OfferValidationAttribute.CATEGORY_ID:
            return lambda category_id: categories.ALL_CATEGORIES_DICT[category_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SUBCATEGORY_ID:
            return lambda subcategory_id: subcategories_v2.ALL_SUBCATEGORIES_DICT[subcategory_id].pro_label
        if sub_rule.attribute == offers_models.OfferValidationAttribute.SHOW_SUB_TYPE:
            return lambda show_sub_type_code: SHOW_SUB_TYPES_LABEL_BY_CODE[int(show_sub_type_code)]
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
            return "grand public"
        case "1":
            return "entre 0 et 3 ans"
        case "2":
            return "entre 3 et 6 ans"
        case "3":
            return "entre 6 et 12 ans"
        case "4":
            return "entre 12 et 16 ans"
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


def install_template_filters(app: Flask) -> None:
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.filters["empty_string_if_null"] = empty_string_if_null
    app.jinja_env.filters["format_amount"] = format_amount
    app.jinja_env.filters["format_booking_cancellation_reason"] = format_booking_cancellation_reason
    app.jinja_env.filters["format_booking_status"] = format_booking_status
    app.jinja_env.filters["format_booking_status_long"] = format_booking_status_long
    app.jinja_env.filters["format_bool"] = format_bool
    app.jinja_env.filters["format_cents"] = format_cents
    app.jinja_env.filters["format_rate"] = format_rate
    app.jinja_env.filters["format_rate_multiply_by_100"] = format_rate_multiply_by_100
    app.jinja_env.filters["format_string_list"] = format_string_list
    app.jinja_env.filters["format_date"] = format_date
    app.jinja_env.filters["format_date_time"] = format_date_time
    app.jinja_env.filters["format_timespan"] = format_timespan
    app.jinja_env.filters["format_deposit_type"] = format_deposit_type
    app.jinja_env.filters["format_offer_validation_status"] = format_offer_validation_status
    app.jinja_env.filters["format_offer_status"] = format_offer_status
    app.jinja_env.filters["format_offer_category"] = format_offer_category
    app.jinja_env.filters["format_subcategories"] = format_subcategories
    app.jinja_env.filters["format_criteria"] = format_criteria
    app.jinja_env.filters["format_tag_object_list"] = format_tag_object_list
    app.jinja_env.filters["format_dms_status"] = format_dms_status
    app.jinja_env.filters["format_graphql_application_status"] = format_graphql_application_status
    app.jinja_env.filters["format_fraud_check_url"] = format_fraud_check_url
    app.jinja_env.filters["format_fraud_action_dict_url"] = format_fraud_action_dict_url
    app.jinja_env.filters["format_role"] = format_role
    app.jinja_env.filters["format_state"] = format_state
    app.jinja_env.filters["format_reason_label"] = format_reason_label
    app.jinja_env.filters["format_adage_referred"] = format_adage_referred
    app.jinja_env.filters["format_modified_info_value"] = format_modified_info_value
    app.jinja_env.filters["format_offer_validation_sub_rule"] = format_offer_validation_sub_rule
    app.jinja_env.filters["format_offer_validation_operator"] = format_offer_validation_operator
    app.jinja_env.filters["get_comparated_format_function"] = get_comparated_format_function
    app.jinja_env.filters["format_offer_types"] = format_offer_types
    app.jinja_env.filters["format_website"] = format_website
    app.jinja_env.filters["format_venue_target"] = format_venue_target
    app.jinja_env.filters["format_titelive_id_lectorat"] = format_titelive_id_lectorat
    app.jinja_env.filters["format_date_range"] = format_date_range
    app.jinja_env.filters["parse_referrer"] = parse_referrer
    app.jinja_env.filters["unescape"] = html.unescape
    app.jinja_env.filters["action_to_name"] = action_to_name
    app.jinja_env.filters["pc_pro_offer_link"] = urls.build_pc_pro_offer_link
    app.jinja_env.filters["pc_pro_offerer_link"] = urls.build_pc_pro_offerer_link
    app.jinja_env.filters["pc_pro_venue_bookings_link"] = urls.build_pc_pro_venue_bookings_link
    app.jinja_env.filters["pc_pro_venue_offers_link"] = urls.build_pc_pro_venue_offers_link
    app.jinja_env.filters["pc_pro_venue_link"] = urls.build_pc_pro_venue_link
    app.jinja_env.filters["pc_pro_user_email_validation_link"] = urls.build_pc_pro_user_email_validation_link
    app.jinja_env.filters["pc_backoffice_public_account_link"] = urls.build_backoffice_public_account_link
    app.jinja_env.filters[
        "pc_backoffice_public_account_link_in_comment"
    ] = urls.build_backoffice_public_account_link_in_comment
