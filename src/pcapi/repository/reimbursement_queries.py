from collections import namedtuple
from datetime import date
from typing import Optional

from sqlalchemy import Date
from sqlalchemy import cast
from sqlalchemy import subquery
from sqlalchemy.orm import aliased

from pcapi.core.bookings.models import Booking
from pcapi.core.offerers.models import Offerer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.users.models import User
from pcapi.models import PaymentStatus
from pcapi.models import Venue
from pcapi.models.payment import Payment
from pcapi.models.payment_status import TransactionStatus


def find_all_offerer_payments(
    offerer_id: int, reimbursement_period: tuple[date, date], venue_id: Optional[int] = None
) -> list[namedtuple]:
    payment_status_query = _build_payment_status_subquery(reimbursement_period)
    payment_query = (
        Payment.query.join(payment_status_query)
        .reset_joinpoint()
        .join(Booking)
        .join(User)
        .reset_joinpoint()
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .filter(Venue.managingOffererId == offerer_id)
    )
    if venue_id:
        payment_query = payment_query.filter(Venue.id == venue_id)

    return (
        payment_query.join(Offerer)
        .distinct(payment_status_query.c.paymentId)
        .order_by(payment_status_query.c.paymentId.desc(), payment_status_query.c.date.desc())
        .with_entities(
            User.lastName.label("user_lastName"),
            User.firstName.label("user_firstName"),
            Booking.token.label("booking_token"),
            Booking.dateUsed.label("booking_dateUsed"),
            Booking.quantity.label("booking_quantity"),
            Booking.amount.label("booking_amount"),
            Offer.name.label("offer_name"),
            Offerer.address.label("offerer_address"),
            Venue.name.label("venue_name"),
            Venue.siret.label("venue_siret"),
            Venue.address.label("venue_address"),
            Payment.amount.label("amount"),
            Payment.reimbursementRate.label("reimbursement_rate"),
            Payment.iban.label("iban"),
            Payment.transactionLabel.label("transactionLabel"),
            payment_status_query.c.status.label("status"),
            payment_status_query.c.detail.label("detail"),
        )
        .all()
    )


def _build_payment_status_subquery(reimbursement_period: tuple[date, date]) -> subquery:
    payment_alias = aliased(Payment)
    payment_date = cast(PaymentStatus.date, Date)
    return (
        PaymentStatus.query.filter(PaymentStatus.paymentId == payment_alias.id)
        .filter(
            PaymentStatus.status == TransactionStatus.SENT,
            payment_date.between(*reimbursement_period, symmetric=True),
        )
        .with_entities(
            PaymentStatus.paymentId.label("paymentId"),
            PaymentStatus.status.label("status"),
            PaymentStatus.detail.label("detail"),
            PaymentStatus.date.label("date"),
        )
        .subquery()
    )


# TODO : delete this legacy function when feature PRO_REIMBURSEMENTS_FILTERS is deleted or activate in production
def legacy_find_all_offerer_payments(offerer_id: int) -> list[namedtuple]:
    payment_status_query = _legacy_build_payment_status_subquery()

    return (
        Payment.query.join(payment_status_query)
        .reset_joinpoint()
        .join(Booking)
        .join(User)
        .reset_joinpoint()
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .filter(Venue.managingOffererId == offerer_id)
        .join(Offerer)
        .distinct(payment_status_query.c.paymentId)
        .order_by(payment_status_query.c.paymentId.desc(), payment_status_query.c.date.desc())
        .with_entities(
            User.lastName.label("user_lastName"),
            User.firstName.label("user_firstName"),
            Booking.token.label("booking_token"),
            Booking.dateUsed.label("booking_dateUsed"),
            Booking.quantity.label("booking_quantity"),
            Booking.amount.label("booking_amount"),
            Offer.name.label("offer_name"),
            Offerer.address.label("offerer_address"),
            Venue.name.label("venue_name"),
            Venue.siret.label("venue_siret"),
            Venue.address.label("venue_address"),
            Payment.amount.label("amount"),
            Payment.reimbursementRate.label("reimbursement_rate"),
            Payment.iban.label("iban"),
            Payment.transactionLabel.label("transactionLabel"),
            payment_status_query.c.status.label("status"),
            payment_status_query.c.detail.label("detail"),
        )
        .all()
    )


# TODO : delete this legacy function when feature PRO_REIMBURSEMENTS_FILTERS is deleted or activate in production
def _legacy_build_payment_status_subquery() -> subquery:
    payment_alias = aliased(Payment)
    return (
        PaymentStatus.query.filter(PaymentStatus.paymentId == payment_alias.id)
        .with_entities(
            PaymentStatus.paymentId.label("paymentId"),
            PaymentStatus.status.label("status"),
            PaymentStatus.detail.label("detail"),
            PaymentStatus.date.label("date"),
        )
        .subquery()
    )
