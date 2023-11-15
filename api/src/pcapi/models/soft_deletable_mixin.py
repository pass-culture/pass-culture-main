from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.orm import declarative_mixin, Mapped
from sqlalchemy.sql import expression


@declarative_mixin
class SoftDeletableMixin:
    isSoftDeleted: Mapped["bool"] = Column(Boolean, nullable=False, default=False, server_default=expression.false())
