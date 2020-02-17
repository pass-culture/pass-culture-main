from collections import namedtuple
from typing import List

from sqlalchemy import subquery
from sqlalchemy.orm import aliased

from models import User, Offerer, PaymentStatus
from models.booking import Booking
from models.offer import Offer
from models.payment import Payment
from models.stock import Stock
from models.venue import Venue


def find_all_offerer_payments(offerer_id: int) -> List[namedtuple]:
    payment_status_query = _build_payment_status_subquery()

    return Payment.query \
        .join(payment_status_query) \
        .reset_joinpoint() \
        .join(Booking) \
        .join(User) \
        .reset_joinpoint() \
        .join(Stock) \
        .join(Offer) \
        .join(Venue) \
        .filter(Venue.managingOffererId == offerer_id) \
        .join(Offerer) \
        .distinct(payment_status_query.c.paymentId) \
        .order_by(payment_status_query.c.paymentId.desc(),
                  payment_status_query.c.date.desc()) \
        .with_entities(User.lastName.label('user_lastName'),
                       User.firstName.label('user_firstName'),
                       Booking.token.label('booking_token'),
                       Booking.dateUsed.label('booking_dateUsed'),
                       Offer.name.label('offer_name'),
                       Offerer.address.label('offerer_address'),
                       Venue.name.label('venue_name'),
                       Venue.siret.label('venue_siret'),
                       Venue.address.label('venue_address'),
                       Payment.amount.label('amount'),
                       Payment.iban.label('iban'),
                       Payment.transactionLabel.label('transactionLabel'),
                       payment_status_query.c.status.label('status'),
                       payment_status_query.c.detail.label('detail')) \
        .all()


def _build_payment_status_subquery() -> subquery:
    payment_alias = aliased(Payment)
    return PaymentStatus.query \
        .filter(PaymentStatus.paymentId == payment_alias.id) \
        .with_entities(PaymentStatus.paymentId.label('paymentId'),
                       PaymentStatus.status.label('status'),
                       PaymentStatus.detail.label('detail'),
                       PaymentStatus.date.label('date')) \
        .subquery()
