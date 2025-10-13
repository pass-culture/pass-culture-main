"""has address mixin"""

import sqlalchemy.orm as sa_orm
from sqlalchemy import String


@sa_orm.declarative_mixin
class HasAddressMixin:
    _address: sa_orm.Mapped[str | None] = sa_orm.mapped_column("address", String(200), nullable=True)

    postalCode: sa_orm.Mapped[str | None] = sa_orm.mapped_column(String(6), nullable=True, index=True)

    city: sa_orm.Mapped[str | None] = sa_orm.mapped_column(String(50), nullable=True)
