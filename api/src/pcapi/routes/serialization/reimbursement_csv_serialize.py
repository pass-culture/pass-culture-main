from collections import namedtuple
import csv
from datetime import date
import decimal
from io import StringIO
from typing import Callable
from typing import Iterable
from typing import Optional
from typing import Union

from pydantic.main import BaseModel

import pcapi.core.finance.api as finance_api
import pcapi.core.finance.utils as finance_utils
from pcapi.core.offers.serialize import serialize_offer_type_educational_or_individual
from pcapi.models.api_errors import ApiErrors
from pcapi.repository.reimbursement_queries import find_all_offerers_payments
from pcapi.utils.date import MONTHS_IN_FRENCH


def format_number_as_french(num: Union[int, float]) -> str:
    return str(num).replace(".", ",")


class ReimbursementDetails:
    CSV_HEADER = [
        "Année",
        "Virement",
        "Créditeur",
        "SIRET créditeur",
        "Adresse créditeur",
        "IBAN",
        "Raison sociale du lieu",
        "Nom de l'offre",
        "Nom utilisateur",
        "Prénom utilisateur",
        "Contremarque",
        "Date de validation de la réservation",
        "Montant de la réservation",
        "Barème",
        "Montant remboursé",
        "Statut du remboursement",
        "Type d'offre",
    ]

    def __init__(self, payment_info: namedtuple):
        # FIXME (dbaty, 2021-01-14): once we have created
        # pricing+cashflow data for pre-2022 payments, remove handling
        # of legacy Payment data from this function.

        using_legacy_models = hasattr(payment_info, "transactionLabel")

        if using_legacy_models:
            # Turn "pass Culture Pro - remboursement 2nde quinzaine 06-2019"
            # into "Décembre : remboursement 2nde quinzaine"
            transfer_infos = payment_info.transactionLabel.replace("pass Culture Pro - ", "").split(" ")
            transfer_label = " ".join(transfer_infos[:-1])
            transfer_date = transfer_infos[-1]
            month_number, year = transfer_date.split("-")
            month_name = MONTHS_IN_FRENCH[int(month_number)]
            self.transfer_name = "{} : {}".format(month_name, transfer_label)
        else:
            year = payment_info.cashflow_date.year
            self.transfer_name = MONTHS_IN_FRENCH[payment_info.cashflow_date.month]
            self.transfer_name += " : remboursement"
            if payment_info.cashflow_date.day >= 16:
                self.transfer_name += " 2nde"
            else:
                self.transfer_name += " 1ère"
            self.transfer_name += " quinzaine"

        self.year = year
        self.venue_name = payment_info.venue_name
        self.venue_siret = payment_info.venue_siret
        self.venue_address = payment_info.venue_address or payment_info.offerer_address
        self.payment_iban = payment_info.iban
        self.venue_name = payment_info.venue_name
        self.offer_name = payment_info.offer_name
        self.user_last_name = payment_info.user_lastName or payment_info.redactor_lastname
        self.user_first_name = payment_info.user_firstName or payment_info.redactor_firstname
        self.booking_token = payment_info.booking_token
        self.booking_used_date = payment_info.booking_dateUsed
        self.booking_total_amount = format_number_as_french(payment_info.booking_amount * payment_info.booking_quantity)
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
                rate = format_number_as_french(rate) + " %"
            else:
                rate = ""
        self.reimbursement_rate = rate
        if using_legacy_models:
            self.reimbursed_amount = format_number_as_french(payment_info.amount)
        else:
            self.reimbursed_amount = format_number_as_french(finance_utils.to_euros(payment_info.amount))
        # Backward compatibility to avoid changing the format of the CSV. This field
        # used to show different statuses.
        self.status = "Remboursement envoyé"
        self.offer_type = serialize_offer_type_educational_or_individual(payment_info.offer_is_educational)

    def as_csv_row(self):
        return [
            self.year,
            self.transfer_name,
            self.venue_name,
            self.venue_siret,
            self.venue_address,
            self.payment_iban,
            self.venue_name,
            self.offer_name,
            self.user_last_name,
            self.user_first_name,
            self.booking_token,
            self.booking_used_date,
            self.booking_total_amount,
            self.reimbursement_rate,
            self.reimbursed_amount,
            self.status,
            self.offer_type,
        ]


def generate_reimbursement_details_csv(reimbursement_details: Iterable[ReimbursementDetails]) -> str:
    output = StringIO()
    csv_lines = [reimbursement_detail.as_csv_row() for reimbursement_detail in reimbursement_details]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(ReimbursementDetails.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def find_all_offerer_reimbursement_details(
    offerer_id: int, reimbursements_period: tuple[Optional[date], Optional[date]], venue_id: Optional[int] = None
) -> list[ReimbursementDetails]:
    return find_all_offerers_reimbursement_details(
        [offerer_id],
        reimbursements_period,
        venue_id=venue_id,
    )


def find_all_offerers_reimbursement_details(
    offerer_ids: list[int], reimbursements_period: tuple[Optional[date], Optional[date]], venue_id: Optional[int] = None
) -> list[ReimbursementDetails]:
    offerer_payments = find_all_offerers_payments(offerer_ids, reimbursements_period, venue_id)
    reimbursement_details = [ReimbursementDetails(offerer_payment) for offerer_payment in offerer_payments]

    return reimbursement_details


def validate_reimbursement_period(
    reimbursement_period_field_names: tuple[str, str], get_query_param: Callable
) -> Union[list[None], list[date]]:
    api_errors = ApiErrors()
    reimbursement_period_dates = []
    for field_name in reimbursement_period_field_names:
        try:
            reimbursement_period_dates.append(date.fromisoformat(get_query_param(field_name)))
        except (TypeError, ValueError):
            api_errors.add_error(field_name, "Vous devez renseigner une date au format ISO (ex. 2021-12-24)")
    if len(api_errors.errors) > 0:
        raise api_errors
    return reimbursement_period_dates or [None, None]


class ReimbursementCsvQueryModel(BaseModel):
    venueId: Optional[str]
    reimbursementPeriodBeginningDate: Optional[str]
    reimbursementPeriodEndingDate: Optional[str]
