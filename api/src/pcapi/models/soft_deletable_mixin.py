import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import expression


@declarative_mixin
class SoftDeletableMixin:
    isSoftDeleted: sa_orm.Mapped[bool] = sa.Column(
        sa.Boolean, nullable=False, default=False, server_default=expression.false()
    )
