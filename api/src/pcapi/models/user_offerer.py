from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from pcapi.models import Model
from pcapi.models.needs_validation_mixin import NeedsValidationMixin
from pcapi.models.pc_object import PcObject


class UserOfferer(PcObject, Model, NeedsValidationMixin):

    userId = Column(BigInteger, ForeignKey("user.id"), primary_key=True)

    user = relationship("User", foreign_keys=[userId], backref=backref("UserOfferers"))

    offererId = Column(BigInteger, ForeignKey("offerer.id"), index=True, primary_key=True)

    offerer = relationship("Offerer", foreign_keys=[offererId], backref=backref("UserOfferers"))

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "offererId",
            name="unique_user_offerer",
        ),
    )
