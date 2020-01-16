import csv
import datetime
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from io import StringIO
from typing import List

from models import Booking, Payment, ThingType
from models.payment_status import TransactionStatus
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

    def is_relevant(self, booking: Booking, **kwargs):
        offer = booking.stock.resolvedOffer
        book_offer = offer.type == str(ThingType.LIVRE_EDITION)
        cinema_card_offer = offer.type == str(ThingType.CINEMA_CARD)
        offer_is_an_exception = book_offer or cinema_card_offer
        return offer.isDigital and not offer_is_an_exception


class PhysicalOffersReimbursement(ReimbursementRule):
    rate = Decimal(1)
    description = 'Remboursement total pour les offres physiques'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        offer = booking.stock.resolvedOffer
        book_offer = offer.type == str(ThingType.LIVRE_EDITION)
        cinema_card_offer = offer.type == str(ThingType.CINEMA_CARD)
        offer_is_an_exception = book_offer or cinema_card_offer
        return offer_is_an_exception or not offer.isDigital


class MaxReimbursementByOfferer(ReimbursementRule):
    rate = Decimal(0)
    description = 'Pas de remboursement au dessus du plafond de 20 000 € par acteur culturel'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        if booking.stock.resolvedOffer.product.isDigital:
            return False
        else:
            return kwargs['cumulative_value'] > 20000


class ReimbursementRateByVenueBetween20000And40000(ReimbursementRule):
    rate = Decimal(0.95)
    description = 'Remboursement à 95% entre 20 000 € et 40 000 € par lieu'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        if booking.stock.resolvedOffer.product.isDigital:
            return False
        else:
            return 20000 < kwargs['cumulative_value'] <= 40000


class ReimbursementRateByVenueBetween40000And100000(ReimbursementRule):
    rate = Decimal(0.85)
    description = 'Remboursement à 85% entre 40 000 € et 100 000 € par lieu'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        if booking.stock.resolvedOffer.product.isDigital:
            return False
        else:
            return 40000 < kwargs['cumulative_value'] <= 100000


class ReimbursementRateByVenueAbove100000(ReimbursementRule):
    rate = Decimal(0.65)
    description = 'Remboursement à 65% au dessus de 100 000 € par lieu'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        if booking.stock.resolvedOffer.product.isDigital:
            return False
        else:
            return kwargs['cumulative_value'] > 100000


class ReimbursementRateForBookAbove20000(ReimbursementRule):
    rate = Decimal(0.95)
    description = 'Remboursement à 95% au dessus de 20 000 € pour les livres'
    valid_from = None
    valid_until = None

    def is_relevant(self, booking: Booking, **kwargs):
        if booking.stock.resolvedOffer.type == str(ThingType.LIVRE_EDITION) \
                and kwargs['cumulative_value'] > 20000:
            return True
        else:
            return False


class ReimbursementRules(Enum):
    DIGITAL_THINGS = DigitalThingsReimbursement()
    PHYSICAL_OFFERS = PhysicalOffersReimbursement()
    BETWEEN_20000_AND_40000_EUROS = ReimbursementRateByVenueBetween20000And40000()
    BETWEEN_40000_AND_100000_EUROS = ReimbursementRateByVenueBetween40000And100000()
    ABOVE_100000_EUROS = ReimbursementRateByVenueAbove100000()
    MAX_REIMBURSEMENT = MaxReimbursementByOfferer()
    BOOK_REIMBURSEMENT = ReimbursementRateForBookAbove20000()


NEW_RULES = [
    ReimbursementRules.DIGITAL_THINGS,
    ReimbursementRules.PHYSICAL_OFFERS,
    ReimbursementRules.BETWEEN_20000_AND_40000_EUROS,
    ReimbursementRules.BETWEEN_40000_AND_100000_EUROS,
    ReimbursementRules.ABOVE_100000_EUROS,
    ReimbursementRules.BOOK_REIMBURSEMENT
]

CURRENT_RULES = [
    ReimbursementRules.DIGITAL_THINGS,
    ReimbursementRules.PHYSICAL_OFFERS,
    ReimbursementRules.MAX_REIMBURSEMENT
]


class AppliedReimbursement:
    def __init__(self, reimbursement_rule: ReimbursementRules, reimbursed_amount: Decimal):
        self.rule = reimbursement_rule
        self.amount = reimbursed_amount


class BookingReimbursement:
    def __init__(self, booking: Booking, reimbursement: ReimbursementRules, reimbursed_amount: Decimal):
        self.booking = booking
        self.reimbursement = reimbursement
        self.reimbursed_amount = reimbursed_amount


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

            payment_current_status = payment.currentStatus.status
            payment_current_status_details = payment.currentStatus.detail

            human_friendly_status = self._get_reimbursement_current_status_in_details(payment_current_status,
                                                                                      payment_current_status_details)

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


def find_all_booking_reimbursements(bookings: List[Booking],
                                    active_rules: List[ReimbursementRules]) -> List[BookingReimbursement]:
    reimbursements = []
    cumulative_bookings_value_by_year = {}

    for booking in bookings:
        booking_civil_year = booking.dateCreated.year
        if booking_civil_year not in cumulative_bookings_value_by_year:
            cumulative_bookings_value_by_year[booking_civil_year] = 0

        if ReimbursementRules.PHYSICAL_OFFERS.value.is_relevant(booking):
            cumulative_bookings_value_by_year[booking_civil_year] = cumulative_bookings_value_by_year[
                                                                booking_civil_year] + booking.value

        potential_rules = _find_potential_rules(booking, active_rules,
                                                cumulative_bookings_value_by_year[booking_civil_year])
        elected_rule = determine_elected_rule(booking, potential_rules)
        reimbursements.append(BookingReimbursement(booking, elected_rule.rule, elected_rule.amount))

    return reimbursements


def determine_elected_rule(booking: Booking, potential_rules: List[AppliedReimbursement]) -> AppliedReimbursement:
    if any(map(lambda r: r.rule == ReimbursementRules.BOOK_REIMBURSEMENT, potential_rules)):
        elected_rule = AppliedReimbursement(ReimbursementRules.BOOK_REIMBURSEMENT,
                                            ReimbursementRules.BOOK_REIMBURSEMENT.value.apply(booking))
    else:
        elected_rule = min(potential_rules, key=lambda x: x.amount)
    return elected_rule


def _find_potential_rules(booking: Booking,
                          rules: List[ReimbursementRules],
                          cumulative_bookings_value: Decimal):
    relevant_rules = []
    for rule in rules:
        if rule.value.is_active and rule.value.is_relevant(booking, cumulative_value=cumulative_bookings_value):
            reimbursed_amount = rule.value.apply(booking)
            relevant_rules.append(AppliedReimbursement(rule, reimbursed_amount))
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
