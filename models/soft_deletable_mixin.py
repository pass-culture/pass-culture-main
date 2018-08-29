from sqlalchemy import Column, Boolean


class SoftDeletableMixin(object):
    isSoftDeleted = Column(Boolean, nullable=False, default=False)

    @property
    def queryNotDeleted(self):
        return self.query.filter_by(isSoftDeleted=False)

