import csv
import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from io import StringIO
from typing import List

from models import Booking, Payment, ThingType
from utils.date import english_to_french_month

MIN_DATETIME = datetime.datetime(datetime.MINYEAR, 1, 1)
MAX_DATETIME = datetime.datetime(datetime.MAXYEAR, 1, 1)

class ReimbursementRule(ABC):
    def is_active(self, booking: Booking):
        valid_from = self.valid_from if self.valid_from else MIN_DATETIME
        valid_until = self.valid_until if self.valid_until else MAX_DATETIME
        return valid_from < booking.dateCreated < valid_until

    @abstractmethod
    def is_relevant(self, booking: Booking, **kwargs):
        pass

    @property
    @abstractmethod
    def rate(self):
        pass

    @property
    @abstractmethod
    def valid_from(self):
        pass

    @property
    @abstractmethod
    def valid_until(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    def apply(self, booking: Booking):
        return Decimal(booking.value * self.rate)


class DigitalThingsReimbursement(ReimbursementRule):
    rate = Decimal(0)
    description = 'Pas de remboursement pour les offres digitales'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking, **kwargs):
        product = booking.stock.resolvedOffer.product
        book_offer = product.type == str(ThingType.LIVRE_EDITION)
        return booking.stock.resolvedOffer.product.isDigital and not book_offer


class PhysicalOffersReimbursement(ReimbursementRule):
    rate = Decimal(1)
    description = 'Remboursement total pour les offres physiques'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking, **kwargs):
        product = booking.stock.resolvedOffer.product
        book_offer = product.type == str(ThingType.LIVRE_EDITION)
        return book_offer or not product.isDigital


class MaxReimbursementByOfferer(ReimbursementRule):
    rate = Decimal(0)
    description = 'Pas de remboursement au dessus du plafond de 20 000 € par offreur'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking, **kwargs):
        if booking.stock.resolvedOffer.product.isDigital:
            return False
        else:
            return kwargs['cumulative_value'] > 20000


class ReimbursementRules(Enum):
    DIGITAL_THINGS = DigitalThingsReimbursement()
    PHYSICAL_OFFERS = PhysicalOffersReimbursement()
    MAX_REIMBURSEMENT = MaxReimbursementByOfferer()


class BookingReimbursement:
    def __init__(self, booking: Booking, reimbursement: ReimbursementRules, reimbursed_amount: Decimal):
        self.booking = booking
        self.reimbursement = reimbursement
        self.reimbursed_amount = reimbursed_amount

    def as_dict(self, include=None):
        dict_booking = self.booking.as_dict(include=include)
        dict_booking['token'] = dict_booking['token'] if dict_booking['isUsed'] else None
        dict_booking['reimbursed_amount'] = self.reimbursed_amount
        dict_booking['reimbursement_rule'] = self.reimbursement.value.description
        return dict_booking


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

    def _get_current_status(self, current_status, current_status_details):
        statuses = {
        'TransactionStatus.PENDING': 'Remboursement en cours',
        'TransactionStatus.NOT_PROCESSABLE': 'Remboursement impossible',
        'TransactionStatus.SENT': 'Remboursé',
        'TransactionStatus.ERROR': 'Erreur',
        'TransactionStatus.RETRY': 'Remboursement retenté',
        'TransactionStatus.BANNED': 'Banni'
        }

        human_friendly_status = statuses.get(current_status)

        if current_status_details is None:
            current_status_details = ""
        else:
            current_status_details = f": {current_status_details}"

        return human_friendly_status + current_status_details


    def __init__(self, payment: Payment = None, booking_used_date: datetime = None):

        if payment is not None:
            booking = payment.booking
            user = booking.user
            offer = booking.stock.resolvedOffer
            venue = offer.venue
            offerer = venue.managingOfferer

            transfer_infos = payment.transactionLabel \
                                    .replace('pass Culture Pro - ', '') \
                                    .split(' ')
            transfer_label = " ".join(transfer_infos[:-1])

            date = transfer_infos[-1]
            [month_number, year] = date.split('-')
            french_month = english_to_french_month(int(year), int(month_number))

            current_status = str(payment.currentStatus.status)
            current_status_details = payment.currentStatus.detail

            human_friendly_status = self._get_current_status(current_status, current_status_details)

            self.year = year
            self.transfer_name = "{} : {}".format(
                french_month,
                transfer_label
            )
            self.venue_name = venue.name
            self.venue_siret = venue.siret
            self.venue_address = venue.address or offerer.address
            self.payment_iban = payment.iban
            self.venue_name = venue.name
            self.offer_name = offer.name
            self.user_last_name = user.lastName
            self.user_first_name = user.firstName
            self.booking_token = booking.token
            self.booking_used_date = booking_used_date
            self.reimbursed_amount = payment.amount
            self.status = human_friendly_status

    def as_csv_row(self):
        return [
            self.year,
            self.transfer_name,
            self.venue_name,
            str(self.venue_siret),
            self.venue_address,
            self.payment_iban,
            self.venue_name,
            self.offer_name,
            self.user_last_name,
            self.user_first_name,
            self.booking_token,
            self.booking_used_date,
            str(self.reimbursed_amount),
            self.status
        ]

def find_all_booking_reimbursements(bookings):
    reimbursements = []
    cumulative_bookings_value = 0

    for booking in bookings:
        if ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking):
            cumulative_bookings_value = cumulative_bookings_value + booking.value

        potential_rules = _find_potential_rules(booking, cumulative_bookings_value)
        elected_rule = min(potential_rules, key=lambda x: x['amount'])
        reimbursements.append(BookingReimbursement(booking, elected_rule['rule'], elected_rule['amount']))

    return reimbursements

def _find_potential_rules(booking, cumulative_bookings_value):
    relevant_rules = []
    for rule in ReimbursementRules:
        if rule.value.is_active and rule.value.is_relevant(booking, cumulative_value=cumulative_bookings_value):
            reimbursed_amount = rule.value.apply(booking)
            relevant_rules.append({'rule': rule, 'amount': reimbursed_amount})
    return relevant_rules

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
