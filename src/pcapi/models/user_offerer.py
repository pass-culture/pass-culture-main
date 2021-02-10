""" user offerer """
import enum

from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject


class RightsType(enum.Enum):
    admin = "admin"
    editor = "editor"


class UserOfferer(PcObject, Model, NeedsValidationMixin):

    userId = Column(BigInteger, ForeignKey("user.id"), primary_key=True)

    user = relationship("User", foreign_keys=[userId], backref=backref("UserOfferers"))

    offererId = Column(BigInteger, ForeignKey("offerer.id"), index=True, primary_key=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref=backref("UserOfferers"))

    # FIXME (dbaty, 2021-02-15): after v123 has been deployed, remove:
    # - this field
    # - RightsType above
    # - the "rightstype" column type in the database
    rights = Column(Enum(RightsType))

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "offererId",
            name="unique_user_offerer",
        ),
    )
