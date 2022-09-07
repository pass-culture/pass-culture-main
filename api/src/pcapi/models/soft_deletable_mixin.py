from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.orm import declarative_mixin
from sqlalchemy.sql import expression


@declarative_mixin
class SoftDeletableMixin:
    isSoftDeleted: bool = Column(Boolean, nullable=False, default=False, server_default=expression.false())
