from sqlalchemy import Boolean
from sqlalchemy import Column


class SoftDeletableMixin(object):
    isSoftDeleted = Column(Boolean, nullable=False, default=False)

