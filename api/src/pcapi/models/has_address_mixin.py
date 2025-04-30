"""has address mixin"""

from sqlalchemy import Column
from sqlalchemy import String
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class HasAddressMixin:
    _address = Column("address", String(200), nullable=True)

    postalCode: sa_orm.Mapped[str] = Column(String(6), nullable=False, index=True)

    city: sa_orm.Mapped[str] = Column(String(50), nullable=False)
