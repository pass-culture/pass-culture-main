""" user offerer """
import enum

from sqlalchemy import BigInteger, Column, Enum, ForeignKey
from sqlalchemy.orm import backref, relationship

from models.needs_validation_mixin import NeedsValidationMixin
from models.pc_object import PcObject


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


class UserOfferer(PcObject, NeedsValidationMixin):

    userId = Column(BigInteger,
                    ForeignKey('user.id'),
                    primary_key=True)

    user = relationship('User',
                        foreign_keys=[userId],
                        backref=backref("UserOfferers"))

    offererId = Column(BigInteger,
                       ForeignKey('offerer.id'),
                       index=True,
                       primary_key=True)

    offerer = relationship('Offerer',
                           foreign_keys=[offererId],
                           backref=backref("UserOfferers"))

    rights = Column(Enum(RightsType))
