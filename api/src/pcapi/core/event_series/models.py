import datetime
import typing

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
    eventSeriesId: sa_orm.Mapped[str] = sa_orm.mapped_column(
        sa.Text, sa.ForeignKey("event_series.id", ondelete="CASCADE"), nullable=False
    )
    eventSeries: sa_orm.Mapped["EventSeries"] = sa_orm.relationship("EventSeries", foreign_keys=[eventSeriesId])
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), nullable=False
    )
    offer: sa_orm.Mapped["Offer"] = sa_orm.relationship("Offer", foreign_keys=[offerId], viewonly=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    dateModified: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()
    )

    __table_args__ = (UniqueConstraint("offerId", name="unique_offer_id_constraint"),)


class EventSeries(Model):
    __tablename__ = "event_series"
    id: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, primary_key=True, nullable=False)
    name = sa_orm.mapped_column(sa.Text, nullable=False)
    description = sa_orm.mapped_column(sa.Text, nullable=True)
    mediationUuid = sa_orm.mapped_column(sa.Text, nullable=True)
    dateCreated: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, server_default=sa.func.now()
    )
    dateModified: sa_orm.Mapped[datetime.datetime] = sa_orm.mapped_column(
        sa.DateTime, nullable=False, onupdate=sa.func.now(), server_default=sa.func.now()
    )

    @property
    def mediationUrl(self) -> str | None:
        if self.mediationUuid:
            return f"{settings.GCP_BUCKET_NAME}/{settings.ARTIST_THUMBS_FOLDER_NAME}/{self.mediationUuid}"
        return None
