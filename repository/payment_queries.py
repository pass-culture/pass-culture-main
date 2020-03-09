from typing import List, Optional

from flask import render_template
from sqlalchemy import text

from domain.payments import keep_only_not_processable_payments
from models import Venue, PaymentMessage, Payment, PaymentStatus, BankInformation, Offerer, Booking, Stock, Offer
from models.db import db
from models.payment_status import TransactionStatus


def find_message_checksum(message_name: str) -> str:
    message = PaymentMessage.query.filter_by(name=message_name).first()
    return message.checksum if message else None


def find_error_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='ERROR')
    error_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query.filter(Payment.id.in_(error_payment_ids)).all()


def find_retry_payments() -> List[Payment]:
    query = render_template('sql/find_payment_ids_with_last_status.sql', status='RETRY')
    retry_payment_ids = db.session.query(PaymentStatus.paymentId).from_statement(text(query)).all()
    return Payment.query.filter(Payment.id.in_(retry_payment_ids)).all()


def find_payments_by_message(message_name: str) -> List[Payment]:
    return Payment.query \
        .join(PaymentMessage) \
        .filter(PaymentMessage.name == message_name) \
        .all()


def _keep_only_venues_with_no_bank_information(query):
    query = query.filter(Venue.bankInformation == None)
    return query


def get_payments_by_message_id(payment_message_id: str) -> List[Payment]:
    payment_query = Payment.query.join(PaymentMessage).filter(PaymentMessage.name == payment_message_id)
    return payment_query.all()


def find_by_booking_id(booking_id: int) -> Optional[Payment]:
    return Payment.query.filter_by(bookingId=booking_id).first()


def find_not_processable_with_bank_information():
    most_recent_payment_status = PaymentStatus.query\
        .with_entities(PaymentStatus.id)\
        .distinct(PaymentStatus.paymentId)\
        .order_by(PaymentStatus.paymentId, PaymentStatus.date.desc())\
        .subquery()

    not_processable_payment_ids = PaymentStatus.query\
        .with_entities(PaymentStatus.paymentId)\
        .filter(PaymentStatus.id.in_(most_recent_payment_status))\
        .filter_by(status=TransactionStatus.NOT_PROCESSABLE)\
        .subquery()

    predicate_matches_venue_or_offerer = (Venue.id == BankInformation.venueId) | (
            Offerer.id == BankInformation.offererId)

    not_processable_payments_with_bank_information = Payment.query\
        .filter(Payment.id.in_(not_processable_payment_ids))\
        .join(Booking)\
        .join(Stock)\
        .join(Offer)\
        .join(Venue)\
        .join(Offerer)\
        .join(BankInformation, predicate_matches_venue_or_offerer)\
        .all()

    return keep_only_not_processable_payments(not_processable_payments_with_bank_information)
