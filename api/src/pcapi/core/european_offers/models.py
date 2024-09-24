import datetime
import decimal
import logging
import typing

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import mutable as sa_mutable

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


logger = logging.getLogger(__name__)


class LangField(typing.TypedDict):
    en: str | None
    fr: str | None
    it: str | None


class EuropeanOffer(PcObject, Base, Model):
    __tablename__ = "european_offer"

    # description
    imageAlt: LangField | None = sa.Column("imageAlt", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    title: LangField | None = sa.Column("title", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    description: LangField | None = sa.Column("description", sa_mutable.MutableDict.as_mutable(postgresql.JSONB))
    date: datetime.datetime | None = sa.Column(sa.DateTime, nullable=True, default=datetime.datetime.utcnow)
    imageUrl: str | None = sa.Column(sa.Text, nullable=True)
    # order
    currency: str = sa.Column(sa.Text, nullable=True)
    price: decimal.Decimal = sa.Column(sa.Numeric(10, 2), nullable=False)
    externalUrl: str | None = sa.Column(sa.Text, nullable=True)
    # address
    country: str | None = sa.Column(sa.Text, nullable=True)
    street: str | None = sa.Column(sa.Text, nullable=True)
    city: str | None = sa.Column(sa.Text, nullable=True)
    zipcode: str | None = sa.Column(sa.Text, nullable=True)
    latitude: decimal.Decimal = sa.Column(sa.Numeric(8, 5), nullable=False)
    longitude: decimal.Decimal = sa.Column(sa.Numeric(8, 5), nullable=False)
