from collections import namedtuple
import csv
from io import StringIO
from typing import Optional

from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.utils.date import MONTHS_IN_FRENCH


def format_number_as_french(num):
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
    ]

    TRANSACTION_STATUSES_DETAILS = {
        TransactionStatus.PENDING: "Remboursement en cours",
        TransactionStatus.NOT_PROCESSABLE: "Remboursement impossible",
        TransactionStatus.UNDER_REVIEW: "Remboursement en cours",
        TransactionStatus.SENT: "Remboursement envoyé",
        TransactionStatus.ERROR: "Remboursement en cours",
        TransactionStatus.RETRY: "Remboursement à renvoyer",
        TransactionStatus.BANNED: "Remboursement rejeté",
    }

    assert set(TRANSACTION_STATUSES_DETAILS) == set(TransactionStatus)

    def __init__(self, payment_info: namedtuple = None):
        if payment_info is not None:
            transfer_infos = payment_info.transactionLabel.replace("pass Culture Pro - ", "").split(" ")
            transfer_label = " ".join(transfer_infos[:-1])

            date = transfer_infos[-1]
            month_number, year = date.split("-")
            month_name = MONTHS_IN_FRENCH[int(month_number)]

            payment_current_status = payment_info.status
            payment_current_status_details = payment_info.detail

            human_friendly_status = _get_reimbursement_current_status_in_details(
                payment_current_status, payment_current_status_details
            )

            self.year = year
            self.transfer_name = "{} : {}".format(month_name, transfer_label)
            self.venue_name = payment_info.venue_name
            self.venue_siret = payment_info.venue_siret
            self.venue_address = payment_info.venue_address or payment_info.offerer_address
            self.payment_iban = payment_info.iban
            self.venue_name = payment_info.venue_name
            self.offer_name = payment_info.offer_name
            self.user_last_name = payment_info.user_lastName
            self.user_first_name = payment_info.user_firstName
            self.booking_token = payment_info.booking_token
            self.booking_used_date = payment_info.booking_dateUsed
            self.booking_total_amount = format_number_as_french(
                payment_info.booking_amount * payment_info.booking_quantity
            )
            if payment_info.reimbursement_rate:
                reimbursement_rate = f"{int(payment_info.reimbursement_rate * 100)}%"
            else:
                reimbursement_rate = ""
            self.reimbursement_rate = reimbursement_rate
            self.reimbursed_amount = format_number_as_french(payment_info.amount)
            self.status = human_friendly_status

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
        ]


def generate_reimbursement_details_csv(reimbursement_details: list[ReimbursementDetails]) -> str:
    output = StringIO()
    csv_lines = [reimbursement_detail.as_csv_row() for reimbursement_detail in reimbursement_details]
    writer = csv.writer(output, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(ReimbursementDetails.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def find_all_offerer_reimbursement_details(
    offerer_id: int, venue_id: Optional[int] = None
) -> list[ReimbursementDetails]:
    offerer_payments = find_all_offerer_payments(offerer_id, venue_id)
    reimbursement_details = [ReimbursementDetails(offerer_payment) for offerer_payment in offerer_payments]

    return reimbursement_details


def _get_reimbursement_current_status_in_details(current_status: str, current_status_details: str) -> str:
    human_friendly_status = ReimbursementDetails.TRANSACTION_STATUSES_DETAILS.get(current_status)

    if current_status is not TransactionStatus.NOT_PROCESSABLE or not current_status_details:
        return human_friendly_status

    return f"{human_friendly_status} : {current_status_details}"
