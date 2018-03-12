import enum
from flask import current_app as app

db = app.db


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


app.model.RightsType = RightsType


class UserOfferer(app.model.PcObject, db.Model):
    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       primary_key=True)

    user = db.relationship(lambda: app.model.User,
                           foreign_keys=[userId],
                           backref=db.backref("UserOfferers"))

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey('offerer.id'),
                          primary_key=True)

    offerer = db.relationship(lambda: app.model.Offerer,
                              foreign_keys=[offererId],
                              backref=db.backref("UserOfferers"))

    rights = db.Column(db.Enum(RightsType))


app.model.UserOfferer = UserOfferer
