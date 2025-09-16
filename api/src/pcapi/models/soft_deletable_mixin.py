import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.sql import expression


@sa_orm.declarative_mixin
class SoftDeletableMixin:
    isSoftDeleted: sa_orm.Mapped[bool] = sa_orm.mapped_column(
        sa.Boolean, nullable=False, default=False, server_default=expression.false()
    )
