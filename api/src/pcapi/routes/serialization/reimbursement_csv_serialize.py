from collections import namedtuple
import csv
import datetime
import decimal
from io import StringIO
import typing
from typing import Callable
from typing import Iterable

from pydantic.v1 import validator
from pydantic.v1.main import BaseModel
import pytz

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.repository as finance_repository
import pcapi.core.finance.utils as finance_utils
from pcapi.core.offers.serialize import serialize_offer_type_educational_or_individual
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import FeatureToggle
from pcapi.utils.date import MONTHS_IN_FRENCH
from pcapi.utils.date import utc_datetime_to_department_timezone
from pcapi.utils.string import u_nbsp


def format_number_as_french(num: int | float) -> str:
    return str(num).replace(".", ",")


def _build_full_address(street: str | None, postal_code: str | None, city: str | None) -> str:
    return " ".join((street or "", postal_code or "", city or ""))


def _get_validation_period(cutoff: datetime.datetime, is_incident: bool = False) -> str:
    """Indicate the 2-week period during which most(*) bookings have
    been validated that correspond with the requested cutoff.

    If the cutoff is 16/01: "... janvier : 1ère quinzaine".
    If the cutoff is 01/02: "... janvier : 2nde quinzaine".

    (*) most bookings, but not all. Some bookings may have been
    validated months ago, but reimbursed much later because there was
    no bank information yet or because the event had not yet occurred.
    """
    # `cutoff` is the _exclusive_ upper bound of the period (i.e. the
    # first second of the day after the last included day).
    cutoff_day = pytz.utc.localize(cutoff).astimezone(finance_utils.ACCOUNTING_TIMEZONE).date()
    last_day = cutoff_day - datetime.timedelta(days=1)
    month = MONTHS_IN_FRENCH[last_day.month]
    if last_day.day == 15:
        fortnight = "1ère quinzaine"
    else:
        fortnight = "2nde quinzaine"
    return f"{'Incident' if is_incident else 'Validées et remboursables'} sur {month} : {fortnight}"


def _legacy_get_validation_period(transaction_label: str) -> str:
    """Indicate the 2-week period during which most(*) bookings have been
    validated that correspond with the requested `Payment.transactionLabel`.

    Turn "pass Culture Pro - remboursement 1ère quinzaine 06-2019"
    into "Validées et remboursables sur mai : 2nde quinzaine".

    We don't want to show what's in `Payment.transactionLabel`,
    because it was unclear.
    """
    fortnight, month_year = transaction_label.replace("pass Culture Pro - remboursement", "").rsplit(" ", 1)
    label_month_number = int(month_year.split("-")[0])
    if "1ère quinzaine" in fortnight:
        fortnight = "2nde quinzaine"
        period_month = label_month_number - 1 if label_month_number > 1 else 11
    else:
        fortnight = "1ère quinzaine"
        period_month = label_month_number
    month_name = MONTHS_IN_FRENCH[int(period_month)]
    return f"Validées et remboursables sur {month_name} : {fortnight}"


class ReimbursementDetails:
    CSV_HEADER = [
        "Réservations concernées par le remboursement",
        "Date du justificatif",
        "N° du justificatif",
        "N° de virement",
        "Intitulé du compte bancaire",
        "IBAN",
        "Raison sociale du lieu",  # 6
        "Adresse du lieu",
        "SIRET du lieu",  # 8
        "Nom de l'offre",
        "N° de réservation (offre collective)",
        "Nom (offre collective)",
        "Prénom (offre collective)",
        "Nom de l'établissement (offre collective)",
        "Date de l'évènement (offre collective)",
        "Contremarque",
        "Date de validation de la réservation",
        "Intitulé du tarif",
        "Montant de la réservation",
        "Barème",
        "Montant remboursé",
        "Type d'offre",
    ]

    # The argument is not a named tuple, but rather an SQLAlchemy
    # result object, but both are as opaque to mypy, which hence
    # reports "attr-defined" errors on almost every line. Instead of
    # polluting the code with dozens of "ignore" comments, disable
    # typing for the whole method.
    @typing.no_type_check
    def __init__(self, payment_info: namedtuple):

        if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
            self.CSV_HEADER[6:9] = [
                "Raison sociale du partenaire culturel",
                "Adresse de l'offre",
                "SIRET du partenaire culturel",
            ]
        using_legacy_models = hasattr(payment_info, "transaction_label")

        # Validation period
        if using_legacy_models:
            self.validation_period = _legacy_get_validation_period(payment_info.transaction_label)
        else:
            is_incident = getattr(payment_info, "is_incident", False)
            self.validation_period = _get_validation_period(payment_info.cashflow_batch_cutoff, is_incident=is_incident)

        # Invoice info
        if using_legacy_models:
            self.invoice_date = ""
            self.invoice_reference = ""
            self.cashflow_batch_label = ""
        else:
            self.invoice_date = payment_info.invoice_date
            self.invoice_reference = payment_info.invoice_reference
            self.cashflow_batch_label = payment_info.cashflow_batch_label

        # Venue info
        self.venue_name = payment_info.venue_name
        self.venue_common_name = payment_info.venue_common_name
        if FeatureToggle.WIP_ENABLE_OFFER_ADDRESS.is_active():
            self.address = _build_full_address(
                getattr(payment_info, "address_street", None),
                getattr(payment_info, "address_postal_code", None),
                getattr(payment_info, "address_city", None),
            )
        else:
            self.address = _build_full_address(
                payment_info.venue_address,
                payment_info.venue_postal_code,
                payment_info.venue_city,
            )
        self.venue_siret = payment_info.venue_siret

        if using_legacy_models:
            self.bank_account_label = self.venue_common_name
        else:
            self.bank_account_label = payment_info.bank_account_label
        self.iban = payment_info.iban

        # Offer, redactor and booking info
        self.offer_name = payment_info.offer_name
        self.booking_token = getattr(payment_info, "booking_token", None)
        self.booking_used_date = payment_info.booking_used_date
        self.booking_price_category_label = getattr(payment_info, "booking_price_category_label", None)
        self.booking_total_amount = format_number_as_french(
            payment_info.booking_amount * getattr(payment_info, "booking_quantity", 1)
        )

        # Collective offer specific fields
        self.redactor_last_name = getattr(payment_info, "redactor_lastname", "")
        self.redactor_first_name = getattr(payment_info, "redactor_firstname", "")
        self.event_date = getattr(payment_info, "event_date", "")
        self.institution_name = getattr(payment_info, "institution_name", "")
        venue_departement_code = getattr(payment_info, "venue_departement_code", None)
        if self.event_date and venue_departement_code:
            timezoned_event_date = utc_datetime_to_department_timezone(self.event_date, venue_departement_code)
            self.event_date = timezoned_event_date.strftime("%d/%m/%Y %H:%M")

        # Reimbursement rate and amount
        if using_legacy_models:
            if payment_info.reimbursement_rate:
                rate = f"{int(payment_info.reimbursement_rate * 100)}%"
            else:
                rate = ""
        else:  # using Pricing.standardRule or Pricing.customRule
            rule = finance_api.find_reimbursement_rule(payment_info.rule_name or payment_info.rule_id)
            if rule.rate:
                rate = decimal.Decimal(rule.rate * 100).quantize(decimal.Decimal("0.01"))
                if rate == int(rate):  # omit decimals if round number
                    rate = int(rate)
                rate = format_number_as_french(rate) + f"{u_nbsp}%"
            else:
                rate = ""
        self.reimbursement_rate = rate
        if using_legacy_models:
            self.reimbursed_amount = format_number_as_french(payment_info.amount)
        else:
            self.reimbursed_amount = format_number_as_french(finance_utils.to_euros(payment_info.amount))

        self.collective_booking_id = payment_info.collective_booking_id or ""

        # Offer type
        self.offer_type = serialize_offer_type_educational_or_individual(
            offer_is_educational=payment_info.collective_booking_id is not None
        )

    @typing.no_type_check  # see comment for `__init__()` above
    def as_csv_row(self) -> list:
        rows = [
            self.validation_period,
            self.invoice_date,
            self.invoice_reference,
            self.cashflow_batch_label,
            self.bank_account_label,
            self.iban,
            self.venue_name,
            self.address,
            self.venue_siret,
            self.offer_name,
            self.collective_booking_id,
            self.redactor_last_name,
            self.redactor_first_name,
            self.institution_name,
            self.event_date,
            self.booking_token,
            self.booking_used_date,
            self.booking_price_category_label,
            self.booking_total_amount,
            self.reimbursement_rate,
            self.reimbursed_amount,
            self.offer_type,
        ]

        return rows


def generate_reimbursement_details_csv(reimbursement_details: Iterable[ReimbursementDetails]) -> str:
    output = StringIO()
    csv_lines = [reimbursement_detail.as_csv_row() for reimbursement_detail in reimbursement_details]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(ReimbursementDetails.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def find_offerer_reimbursement_details(
    offerer_id: int,
    reimbursements_period: tuple[datetime.date | None, datetime.date | None],
    bank_account_id: int | None = None,
) -> list[ReimbursementDetails]:
    offerer_payments = finance_repository.find_offerer_payments(offerer_id, reimbursements_period, bank_account_id)  # type: ignore[arg-type]
    reimbursement_details = [ReimbursementDetails(offerer_payment) for offerer_payment in offerer_payments]

    return reimbursement_details


def find_reimbursement_details_by_invoices(
    invoices_references: list[str],
) -> list[ReimbursementDetails]:
    offerers_payments = finance_repository.find_offerer_payments(invoices_references=invoices_references)
    reimbursement_details = [ReimbursementDetails(offerer_payment) for offerer_payment in offerers_payments]

    return reimbursement_details


def validate_reimbursement_period(
    reimbursement_period_field_names: tuple[str, str], get_query_param: Callable
) -> tuple[None, ...] | tuple[datetime.date, ...]:
    api_errors = ApiErrors()
    reimbursement_period_dates: tuple[datetime.date, ...] = tuple()
    for field_name in reimbursement_period_field_names:
        try:
            reimbursement_period_dates += (datetime.date.fromisoformat(get_query_param(field_name)),)
        except (TypeError, ValueError):
            api_errors.add_error(field_name, "Vous devez renseigner une date au format ISO (ex. 2021-12-24)")
    if len(api_errors.errors) > 0:
        raise api_errors
    return reimbursement_period_dates or (None, None)


class ReimbursementCsvQueryModel(BaseModel):
    offererId: int
    bankAccountId: int | None
    reimbursementPeriodBeginningDate: str | None
    reimbursementPeriodEndingDate: str | None


class ReimbursementCsvByInvoicesModel(BaseModel):
    invoicesReferences: list[str]

    @validator("invoicesReferences", pre=True)
    def ensure_invoices_references_is_list(cls, v: list[str] | str) -> list[str]:
        if isinstance(v, str):
            return [v]
        return v
