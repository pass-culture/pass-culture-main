import sqlalchemy as sa
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import expression


@declarative_mixin
class SoftDeletableMixin:
    isSoftDeleted: bool = sa.Column(sa.Boolean, nullable=False, default=False, server_default=expression.false())
