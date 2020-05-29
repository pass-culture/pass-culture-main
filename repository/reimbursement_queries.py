from collections import namedtuple
from typing import List

from sqlalchemy import subquery
from sqlalchemy.orm import aliased

from models import UserSQLEntity, Offerer, PaymentStatus
from models.booking_sql_entity import BookingSQLEntity
from models.offer import Offer
from models.payment import Payment
from models.stock_sql_entity import StockSQLEntity
from models import VenueSQLEntity


def find_all_offerer_payments(offerer_id: int) -> List[namedtuple]:
    payment_status_query = _build_payment_status_subquery()

    return Payment.query \
        .join(payment_status_query) \
        .reset_joinpoint() \
        .join(BookingSQLEntity) \
        .join(UserSQLEntity) \
        .reset_joinpoint() \
        .join(StockSQLEntity) \
        .join(Offer) \
        .join(VenueSQLEntity) \
        .filter(VenueSQLEntity.managingOffererId == offerer_id) \
        .join(Offerer) \
        .distinct(payment_status_query.c.paymentId) \
        .order_by(payment_status_query.c.paymentId.desc(),
                  payment_status_query.c.date.desc()) \
        .with_entities(UserSQLEntity.lastName.label('user_lastName'),
                       UserSQLEntity.firstName.label('user_firstName'),
                       BookingSQLEntity.token.label('booking_token'),
                       BookingSQLEntity.dateUsed.label('booking_dateUsed'),
                       Offer.name.label('offer_name'),
                       Offerer.address.label('offerer_address'),
                       VenueSQLEntity.name.label('venue_name'),
                       VenueSQLEntity.siret.label('venue_siret'),
                       VenueSQLEntity.address.label('venue_address'),
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
