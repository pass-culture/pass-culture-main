import typing
import uuid
from datetime import datetime

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy import UniqueConstraint

from pcapi import settings
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from pcapi.core.offers.models import Offer


class EventSeriesOfferLink(PcObject, Model):
    __tablename__ = "event_series_offer_link"

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)
    event_series_id: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("event_series.id", ondelete="CASCADE"), nullable=False
    )
    event_series: sa_orm.Mapped["EventSeries"] = sa_orm.relationship(
        "EventSeries", foreign_keys=[event_series_id], viewonly=True
    )
    offer_id: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offer_id], viewonly=True)
    date_created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_modified: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()
    )

    __table_args__ = (UniqueConstraint("offer_id", name="unique_offer_id_constraint"),)


class EventSeries(Model):
    __tablename__ = "event_series"
    id: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, primary_key=True, nullable=False, default=lambda _: str(uuid.uuid4())
    )
    name = sa_orm.mapped_column(sa.Text, nullable=False)
    description = sa_orm.mapped_column(sa.Text, nullable=True)
    mediation_uuid = sa_orm.mapped_column(sa.Text, nullable=True)
    date_created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    date_modified: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()
    )

    @property
    def mediationUrl(self) -> str | None:
        if self.mediation_uuid:
            return f"{settings.GCP_BUCKET_NAME}/{settings.ARTIST_THUMBS_FOLDER_NAME}/{self.mediation_uuid}"
        return None
