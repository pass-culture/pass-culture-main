import datetime
import enum
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.models import Model
from pcapi.models.pc_object import PcObject
from pcapi.utils import db as db_utils


if typing.TYPE_CHECKING:
    from pcapi.core.offers.models import Offer


class CulturalOutreachStatus(enum.StrEnum):
    PENDING = "PENDING"
    QUALIFIED = "QUALIFIED"
    DISQUALIFIED = "DISQUALIFIED"


class CulturalOutreach(PcObject, Model):
    __tablename__ = "cultural_outreach"

    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False, unique=True
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="culturalOutreach"
    )
    claimedDatetime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    status: sa_orm.Mapped[CulturalOutreachStatus] = sa_orm.mapped_column(
        db_utils.MagicEnum(CulturalOutreachStatus),
        nullable=False,
        default=CulturalOutreachStatus.PENDING,
        server_default=CulturalOutreachStatus.PENDING.value,
        index=True,
    )
