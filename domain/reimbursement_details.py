import datetime

from models.payment_status import TransactionStatus
from utils.date import english_to_french_month


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

    def _get_reimbursement_current_status_in_details(self, current_status: str, current_status_details: str):
        human_friendly_status = ReimbursementDetails.TRANSACTION_STATUSES_DETAILS.get(current_status)

        if current_status_details is None:
            return human_friendly_status

        return f"{human_friendly_status} : {current_status_details}"

    def __init__(self, payment: object = None, booking_used_date: datetime = None):
        if payment is not None:
            transfer_infos = payment.transactionLabel \
                .replace('pass Culture Pro - ', '') \
                .split(' ')
            transfer_label = " ".join(transfer_infos[:-1])

            date = transfer_infos[-1]
            [month_number, year] = date.split('-')
            french_month = english_to_french_month(int(year), int(month_number))

            payment_current_status = payment.status
            payment_current_status_details = payment.detail

            human_friendly_status = self._get_reimbursement_current_status_in_details(payment_current_status,
                                                                                      payment_current_status_details)

            self.year = year
            self.transfer_name = "{} : {}".format(
                french_month,
                transfer_label
            )
            self.venue_name = payment.venue_name
            self.venue_siret = payment.venue_siret
            self.venue_address = payment.venue_address or payment.offerer_address
            self.payment_iban = payment.iban
            self.venue_name = payment.venue_name
            self.offer_name = payment.offer_name
            self.user_last_name = payment.user_lastName
            self.user_first_name = payment.user_firstName
            self.booking_token = payment.booking_token
            self.booking_used_date = booking_used_date
            self.reimbursed_amount = payment.amount
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
