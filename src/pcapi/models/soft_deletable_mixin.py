from sqlalchemy import Boolean
from sqlalchemy import Column


class SoftDeletableMixin:
    isSoftDeleted = Column(Boolean, nullable=False, default=False)
