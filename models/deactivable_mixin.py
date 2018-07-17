import sqlalchemy as db
from sqlalchemy.sql import expression


class DeactivableMixin(object):
    isActive = db.Column(db.Boolean,
                         nullable=False,
                         server_default=expression.true(),
                         default=True)

    @property
    def queryActive(self):
        return self.query.filter_by(isActive=True)
