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
) -> list[tuple]:
    return find_all_offerers_payments(
        offerer_ids=[offerer_id],
        reimbursement_period=reimbursement_period,
        venue_id=venue_id,
    )


def find_all_offerers_payments(
    offerer_ids: list[int], reimbursement_period: tuple[date, date], venue_id: Optional[int] = None
) -> list[tuple]:
    payment_date = cast(PaymentStatus.date, Date)
    sent_payments = (
        Payment.query.join(PaymentStatus)
        .join(Booking)
        .filter(
            PaymentStatus.status == TransactionStatus.SENT,
            payment_date.between(*reimbursement_period, symmetric=True),
            Booking.offererId.in_(offerer_ids),
            Booking.isUsed,
            (Booking.venueId == venue_id) if venue_id else (Booking.venueId is not None),
        )
        .join(Offerer)
        .join(User)
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .distinct(Payment.id)
        .order_by(Payment.id.desc(), PaymentStatus.date.desc())
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
            PaymentStatus.status.label("status"),
            PaymentStatus.detail.label("detail"),
        )
    )

    return sent_payments.all()


# TODO(AnthonySkorski, 2021-09-15): delete this legacy function when feature PRO_REIMBURSEMENTS_FILTERS is deleted or activate in production
def legacy_find_all_offerer_payments(offerer_id: int) -> list[namedtuple]:
    return legacy_find_all_offerers_payments([offerer_id])


# TODO(AnthonySkorski, 2021-09-15): delete this legacy function when feature PRO_REIMBURSEMENTS_FILTERS is deleted or activate in production
def legacy_find_all_offerers_payments(offerer_ids: list[int]) -> list[namedtuple]:
    payment_status_query = _legacy_build_payment_status_subquery()

    query = (
        Payment.query.join(payment_status_query)
        .reset_joinpoint()
        .join(Booking)
        .join(User)
        .reset_joinpoint()
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .filter(Venue.managingOffererId.in_(offerer_ids))
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
    )
    return query.all()


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
