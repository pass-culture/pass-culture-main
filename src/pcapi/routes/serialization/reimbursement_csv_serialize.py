from collections import namedtuple
import csv
from io import StringIO
from typing import List

from pcapi.models.payment_status import TransactionStatus
from pcapi.repository.reimbursement_queries import find_all_offerer_payments
from pcapi.utils.date import english_to_french_month


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
        "Montant remboursé",
        "Statut du remboursement"
    ]

    TRANSACTION_STATUSES_DETAILS = {
        TransactionStatus.PENDING: 'Remboursement initié',
        TransactionStatus.NOT_PROCESSABLE: 'Remboursement impossible',
        TransactionStatus.SENT: 'Remboursement envoyé',
        TransactionStatus.ERROR: 'Erreur d\'envoi du remboursement',
        TransactionStatus.RETRY: 'Remboursement à renvoyer',
        TransactionStatus.BANNED: 'Remboursement rejeté'
    }

    def __init__(self, payment_info: namedtuple = None):
        if payment_info is not None:
            transfer_infos = payment_info.transactionLabel \
                .replace('pass Culture Pro - ', '') \
                .split(' ')
            transfer_label = " ".join(transfer_infos[:-1])

            date = transfer_infos[-1]
            [month_number, year] = date.split('-')
            french_month = english_to_french_month(int(year), int(month_number))

            payment_current_status = payment_info.status
            payment_current_status_details = payment_info.detail

            human_friendly_status = _get_reimbursement_current_status_in_details(payment_current_status,
                                                                                 payment_current_status_details)

            self.year = year
            self.transfer_name = "{} : {}".format(
                french_month,
                transfer_label
            )
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
            self.reimbursed_amount = payment_info.amount
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
            self.reimbursed_amount,
            self.status
        ]


def generate_reimbursement_details_csv(reimbursement_details: List[ReimbursementDetails]):
    output = StringIO()
    csv_lines = [
        reimbursement_detail.as_csv_row()
        for reimbursement_detail in reimbursement_details
    ]
    writer = csv.writer(output, dialect=csv.excel, delimiter=';')
    writer.writerow(ReimbursementDetails.CSV_HEADER)
    writer.writerows(csv_lines)
    return output.getvalue()


def find_all_offerer_reimbursement_details(offerer_id: int) -> List[ReimbursementDetails]:
    offerer_payments = find_all_offerer_payments(offerer_id)
    reimbursement_details = [ReimbursementDetails(offerer_payment) for offerer_payment in offerer_payments]

    return reimbursement_details


def _get_reimbursement_current_status_in_details(current_status: str, current_status_details: str):
    human_friendly_status = ReimbursementDetails.TRANSACTION_STATUSES_DETAILS.get(current_status)

    if current_status_details is None:
        return human_friendly_status

    return f"{human_friendly_status} : {current_status_details}"
