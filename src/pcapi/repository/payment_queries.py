from typing import List, Optional

from flask import render_template
from sqlalchemy import text

from pcapi.domain.payments import keep_only_not_processable_payments
from pcapi.models import BankInformation, BookingSQLEntity, OfferSQLEntity, Offerer, Payment, \
    PaymentMessage, PaymentStatus, StockSQLEntity, VenueSQLEntity
from pcapi.models.db import db
from pcapi.models.payment_status import TransactionStatus
from pcapi.models.bank_information import BankInformationStatus


def find_message_checksum(message_name: str) -> Optional[str]:
    message = PaymentMessage.query \
        .filter_by(name=message_name) \
        .first()
    return message.checksum if message else None


def find_error_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='ERROR')
    error_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query \
        .filter(Payment.id.in_(error_payment_ids)) \
        .all()


def find_retry_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='RETRY')
    retry_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query \
        .filter(Payment.id.in_(retry_payment_ids)) \
        .all()


def find_payments_by_message(message_name: str) -> List[Payment]:
    return Payment.query \
        .join(PaymentMessage) \
        .filter(PaymentMessage.name == message_name) \
        .all()


def get_payments_by_message_id(payment_message_id: str) -> List[Payment]:
    return Payment.query \
        .join(PaymentMessage) \
        .filter(PaymentMessage.name == payment_message_id) \
        .all()


def find_by_booking_id(booking_id: int) -> Optional[Payment]:
    return Payment.query \
        .filter_by(bookingId=booking_id) \
        .first()


def find_not_processable_with_bank_information() -> List[Payment]:
    most_recent_payment_status = PaymentStatus.query \
        .with_entities(PaymentStatus.id) \
        .distinct(PaymentStatus.paymentId) \
        .order_by(PaymentStatus.paymentId, PaymentStatus.date.desc()) \
        .subquery()

    not_processable_payment_ids = PaymentStatus.query \
        .with_entities(PaymentStatus.paymentId) \
        .filter(PaymentStatus.id.in_(most_recent_payment_status)) \
        .filter_by(status=TransactionStatus.NOT_PROCESSABLE) \
        .subquery()

    predicate_matches_venue_or_offerer = ((VenueSQLEntity.id == BankInformation.venueId) | (
        Offerer.id == BankInformation.offererId)) & (BankInformation.status == BankInformationStatus.ACCEPTED)

    not_processable_payments_with_bank_information = Payment.query \
        .filter(Payment.id.in_(not_processable_payment_ids)) \
        .join(BookingSQLEntity) \
        .join(StockSQLEntity) \
        .join(OfferSQLEntity) \
        .join(VenueSQLEntity) \
        .join(Offerer) \
        .join(BankInformation, predicate_matches_venue_or_offerer) \
        .all()

    return keep_only_not_processable_payments(not_processable_payments_with_bank_information)
