"""has address mixin"""

import sqlalchemy.orm as sa_orm
from sqlalchemy import String
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.orm import mapped_column


@declarative_mixin
class HasAddressMixin:
    _address = mapped_column("address", String(200), nullable=True)

    postalCode: sa_orm.Mapped[str] = mapped_column(String(6), nullable=False, index=True)

    city: sa_orm.Mapped[str] = mapped_column(String(50), nullable=False)
