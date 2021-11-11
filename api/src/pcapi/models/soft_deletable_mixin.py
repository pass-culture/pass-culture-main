from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy.sql import expression


class SoftDeletableMixin:
    isSoftDeleted = Column(Boolean, nullable=False, default=False, server_default=expression.false())
