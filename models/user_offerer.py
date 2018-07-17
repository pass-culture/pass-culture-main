import enum

import sqlalchemy as db

from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


class UserOfferer(PcObject,
                  NeedsValidationMixin,
                  db.Model):
    userId = db.Column(db.BigInteger,
                       db.ForeignKey('user.id'),
                       primary_key=True)

    user = db.relationship('User',
                           foreign_keys=[userId],
                           backref=db.backref("UserOfferers"))

    offererId = db.Column(db.BigInteger,
                          db.ForeignKey('offerer.id'),
                          primary_key=True)

    offerer = db.relationship('Offerer',
                              foreign_keys=[offererId],
                              backref=db.backref("UserOfferers"))

    rights = db.Column(db.Enum(RightsType))
