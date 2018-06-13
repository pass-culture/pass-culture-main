from flask import current_app as app
from sqlalchemy.sql import expression

db = app.db


class DeactivableMixin(object):
    isActive = db.Column(db.Boolean,
                         nullable=False,
                         server_default=expression.true(),
                         default=True)

    @property
    def queryActive(self):
        return self.query.filter_by(isActive=True)

app.model.DeactivableMixin = DeactivableMixin
