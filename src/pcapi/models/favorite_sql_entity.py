from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from pcapi.models.db import Model
from pcapi.models.pc_object import PcObject


class FavoriteSQLEntity(PcObject, Model):
    __tablename__ = "favorite"

    userId = Column(BigInteger, ForeignKey("user.id"), index=True, nullable=False)

    user = relationship("UserSQLEntity", foreign_keys=[userId], backref="favorites")

    offerId = Column(BigInteger, ForeignKey("offer.id"), index=True, nullable=False)

    offer = relationship("Offer", foreign_keys=[offerId], backref="favorites")

    mediationId = Column(BigInteger, ForeignKey("mediation.id"), index=True, nullable=True)

    mediation = relationship("Mediation", foreign_keys=[mediationId], backref="favorites")

    __table_args__ = (
        UniqueConstraint(
            "userId",
            "offerId",
            name="unique_favorite",
        ),
    )
