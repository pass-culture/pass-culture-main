""" transfer model """
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, \
    Column, \
    ForeignKey, \
    String, \
    Numeric, \
    Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.db import Model
from models.payment_status import TransactionStatus, PaymentStatus
from models.pc_object import PcObject


class Payment(PcObject, Model):
    id = Column(BigInteger,
                primary_key=True,
                autoincrement=True)

    bookingId = Column(BigInteger,
                       ForeignKey("booking.id"),
                       index=True,
                       nullable=False)

    booking = relationship('Booking',
                           foreign_keys=[bookingId],
                           backref='payments')

    amount = Column(Numeric(10, 2), nullable=False)

    reimbursementRule = Column(String(200), nullable=False)

    reimbursementRate = Column(Numeric(10, 2), nullable=False)

    recipientName = Column(String(140), nullable=False)

    recipientSiren = Column(String(9), nullable=False)

    iban = Column(String(27), nullable=True)

    bic = Column(String(11),
                 CheckConstraint('(iban IS NULL AND bic IS NULL) OR (iban IS NOT NULL AND bic IS NOT NULL)',
                                 name='check_iban_and_bic_xor_not_iban_and_not_bic'),
                 nullable=True)

    comment = Column(Text, nullable=True)

    author = Column(String(27), nullable=False)

    transactionMessageId = Column(String(50), nullable=True)

    transactionEndToEndId = Column(UUID(as_uuid=True), nullable=True)

    def setStatus(self, status: TransactionStatus, detail: str = None):
        payment_status = PaymentStatus()
        payment_status.status = status
        payment_status.date = datetime.utcnow()
        payment_status.detail = detail

        if self.statuses:
            self.statuses.append(payment_status)
        else:
            self.statuses = [payment_status]

    def setTransactionIds(self, message_id: str, end_to_end_id: uuid.UUID):
        self.transactionMessageId = message_id
        self.transactionEndToEndId = end_to_end_id

    def nullifyTransactionIds(self):
        self.transactionMessageId = None
        self.transactionEndToEndId = None


class PaymentDetails:
    CSV_HEADER = [
        "ID de l'utilisateur",
        "Email de l'utlisateur",
        "Raison social de la structure",
        "SIREN",
        "Raison sociale du lieu",
        "SIRET",
        "Nom de l'offre",
        "Type de l'offre",
        "Date de la réservation",
        "Prix de la réservation",
        "Date de validation",
        "IBAN",
        "Message ID",
        "Transaction ID",
        "Taux de remboursement",
        "Montant remboursé à l'offreur",
    ]

    def __init__(self, payment: Payment = None, booking_used_date: datetime = None):
        if payment is not None:
            self.booking_user_id = payment.booking.user.id
            self.booking_user_email = payment.booking.user.email
            self.offerer_name = payment.booking.stock.resolvedOffer.venue.managingOfferer.name
            self.offerer_siren = payment.booking.stock.resolvedOffer.venue.managingOfferer.siren
            self.venue_name = payment.booking.stock.resolvedOffer.venue.name
            self.venue_siret = payment.booking.stock.resolvedOffer.venue.siret
            self.offer_name = payment.booking.stock.resolvedOffer.eventOrThing.name
            self.offer_type = payment.booking.stock.resolvedOffer.eventOrThing.offerType['label']
            self.booking_date = payment.booking.dateCreated
            self.booking_amount = payment.booking.value
            self.booking_used_date = booking_used_date
            self.payment_iban = payment.iban
            self.transaction_message_id = payment.transactionMessageId
            self.transaction_end_to_end_id = payment.transactionEndToEndId
            self.reimbursement_rate = payment.reimbursementRate
            self.reimbursed_amount = payment.amount

    def as_csv_row(self):
        return [
            str(self.booking_user_id),
            self.booking_user_email,
            self.offerer_name,
            self.offerer_siren,
            self.venue_name,
            self.venue_siret,
            self.offer_name,
            self.offer_type,
            str(self.booking_date),
            str(self.booking_amount),
            str(self.booking_used_date),
            self.payment_iban,
            self.transaction_message_id,
            str(self.transaction_end_to_end_id),
            str(self.reimbursement_rate),
            str(self.reimbursed_amount)
        ]
