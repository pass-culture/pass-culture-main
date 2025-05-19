"""deactivable mixin"""

import sqlalchemy.orm as sa_orm
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql import expression


@sa_orm.declarative_mixin
class DeactivableMixin:
    isActive: sa_orm.Mapped[bool] = Column(Boolean, nullable=False, server_default=expression.true(), default=True)
