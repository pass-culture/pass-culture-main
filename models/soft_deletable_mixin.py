from sqlalchemy import Column, Boolean


class SoftDeletableMixin(object):
    isSoftDeleted = Column(Boolean, nullable=False, default=False)

