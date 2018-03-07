from flask import current_app as app

db = app.db


class DeactivableMixin(object):
    isActive = db.Column(db.Boolean, nullable=False, default=True)

app.model.DeactivableMixin = DeactivableMixin
