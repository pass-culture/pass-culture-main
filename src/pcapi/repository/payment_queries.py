import datetime
from typing import Iterable
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import joinedload

from pcapi.core.offerers.models import Offerer
from pcapi.domain.payments import keep_only_not_processable_payments
from pcapi.models import BankInformation
from pcapi.models import Booking
from pcapi.models import Offer
from pcapi.models import Payment
from pcapi.models import PaymentMessage
from pcapi.models import PaymentStatus
from pcapi.models import Stock
from pcapi.models import Venue
from pcapi.models.bank_information import BankInformationStatus
from pcapi.models.db import db
from pcapi.models.payment_status import TransactionStatus


def find_payments_by_message(message_name: str) -> list[Payment]:
    return Payment.query.join(PaymentMessage).filter(PaymentMessage.name == message_name).all()


def has_payment(booking: Booking) -> Optional[Payment]:
    return db.session.query(Payment.query.filter_by(bookingId=booking.id).exists()).scalar()


def find_not_processable_with_bank_information() -> list[Payment]:
    most_recent_payment_status = (
        PaymentStatus.query.with_entities(PaymentStatus.id)
        .distinct(PaymentStatus.paymentId)
        .order_by(PaymentStatus.paymentId, PaymentStatus.date.desc())
        .subquery()
    )

    not_processable_payment_ids = (
        PaymentStatus.query.with_entities(PaymentStatus.paymentId)
        .filter(PaymentStatus.id.in_(most_recent_payment_status))
        .filter_by(status=TransactionStatus.NOT_PROCESSABLE)
        .subquery()
    )

    predicate_matches_venue_or_offerer = (
        (Venue.id == BankInformation.venueId) | (Offerer.id == BankInformation.offererId)
    ) & (BankInformation.status == BankInformationStatus.ACCEPTED)

    not_processable_payments_with_bank_information = (
        Payment.query.filter(Payment.id.in_(not_processable_payment_ids))
        .join(Booking)
        .join(Venue)
        .join(Offerer)
        .join(BankInformation, predicate_matches_venue_or_offerer)
        .all()
    )
    return keep_only_not_processable_payments(not_processable_payments_with_bank_information)


def join_for_payment_details(query):
    return (
        query.options(joinedload(Payment.statuses))
        .options(joinedload(Payment.booking))
        .options(
            joinedload(Payment.booking)
            .joinedload(Booking.stock)
            .joinedload(Stock.offer)
            .joinedload(Offer.venue)
            .joinedload(Venue.managingOfferer)
        )
        .options(
            joinedload(Payment.booking).joinedload(Booking.stock).joinedload(Stock.offer).joinedload(Offer.product)
        )
    )


def _get_payment_ids_with_latest_status(batch_date: datetime.datetime = None):
    """Return a query with each payment id with its latest status,
    filtered on the requested batch date if given.

    This is a helper, to be used as a subquery by other functions in
    this module.
    """
    query = (
        Payment.query.distinct(PaymentStatus.paymentId)
        .join(PaymentStatus)
        .order_by(PaymentStatus.paymentId, PaymentStatus.date.desc())
        .with_entities(Payment.id, PaymentStatus.status)
    )
    if batch_date:
        query = query.filter(Payment.batchDate == batch_date)
    return query


def get_payments_by_status(statuses: Iterable[TransactionStatus], batch_date: datetime.datetime = None):
    """Return a query with payments for which the latest status is one the
    requested statuses.

    If a batch date is given, filter on it.
    """
    ids_and_latest_statuses = _get_payment_ids_with_latest_status(batch_date).subquery()
    # fmt: off
    return (
        Payment.query
        .join(ids_and_latest_statuses, Payment.id == ids_and_latest_statuses.c.id)
        .filter(ids_and_latest_statuses.c.status.in_(statuses))
    )
    # fmt: on


def get_payment_count_by_status(batch_date: datetime.datetime) -> dict[str, int]:
    """Return a dictionary with the number of payments with each (latest)
    status.
    """
    ids_and_latest_statuses = _get_payment_ids_with_latest_status(batch_date).subquery()
    # fmt: off
    query = (
        db.session.query(
            func.distinct(ids_and_latest_statuses.c.status),
            func.count(),
        )
        .group_by(ids_and_latest_statuses.c.status)
    )
    # fmt: on
    return dict(query.all())


def group_by_iban_and_bic(payment_query):
    query = payment_query.group_by(Payment.iban, Payment.bic).with_entities(
        Payment.iban,
        Payment.bic,
        func.sum(Payment.amount).label("total_amount"),
        # recipientName and recipientSiren should be the same for all
        # payments with the same IBAN and BIC.
        func.min(Payment.recipientName).label("recipient_name"),
        func.min(Payment.recipientSiren).label("recipient_siren"),
        # XXX Payments may have a different transactionLabel (for
        # example if a payment that has been generated in a previous
        # run is to be retried alongside a new payment that hence has
        # a different transaction label). I don't know if it was
        # expected in the previous implementation.
        func.min(Payment.transactionLabel).label("transaction_label"),
    )
    return set(query)


def group_by_venue(payment_query) -> list:
    query = (
        payment_query.join(Booking)
        .join(Stock)
        .join(Offer)
        .join(Venue)
        .join(Offerer)
        .group_by(Venue.id, Offerer.name, Offerer.siren, Payment.iban, Payment.bic)
        .with_entities(
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
            Venue.siret.label("siret"),
            Offerer.name.label("offerer_name"),
            Offerer.siren.label("siren"),
            Payment.iban.label("iban"),
            Payment.bic.label("bic"),
            func.sum(Payment.amount).label("total_amount"),
        )
        .order_by(Venue.id)
    )
    return list(query)
