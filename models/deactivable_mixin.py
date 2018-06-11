from flask import current_app as app

db = app.db


class DeactivableMixin(object):
    isActive = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def queryActive(self):
        return self.query.filter_by(isActive=True)

app.model.DeactivableMixin = DeactivableMixin
