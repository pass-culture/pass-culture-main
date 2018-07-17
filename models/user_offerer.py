import enum
from flask import current_app as app

db = app.db


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


RightsType = RightsType


class UserOfferer(PcObject,
                  NeedsValidationMixin,
                  db.Model):
    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       primary_key=True)

    user = db.relationship(lambda: User,
                           foreign_keys=[userId],
                           backref=db.backref("UserOfferers"))

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey('offerer.id'),
                          primary_key=True)

    offerer = db.relationship(lambda: Offerer,
                              foreign_keys=[offererId],
                              backref=db.backref("UserOfferers"))

    rights = db.Column(db.Enum(RightsType))


UserOfferer = UserOfferer
