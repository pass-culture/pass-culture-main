""" has address mixin """

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy.orm import declarative_mixin
from sqlalchemy import orm as sa_orm


@declarative_mixin
class HasAddressMixin:
    address = Column(String(200), nullable=True)

    postalCode: sa_orm.Mapped[str] = Column(String(6), nullable=False, index=True)

    city: sa_orm.Mapped[str] = Column(String(50), nullable=False, index=True)
