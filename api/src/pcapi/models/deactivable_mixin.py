"""deactivable mixin"""

import sqlalchemy.orm as sa_orm
from sqlalchemy import Boolean
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import expression


@sa_orm.declarative_mixin
class DeactivableMixin:
    isActive: sa_orm.Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=expression.true(), default=True
    )
