import datetime
import typing

import psycopg2.extras
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from sqlalchemy.dialects import postgresql

from pcapi import settings
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    import pcapi.core.criteria.models as criteria_models
    import pcapi.core.offers.models as offers_models


class Highlight(PcObject, Model):
    """
    Model containing DateRange fields.

    ⚠️ PostgreSQL stores DateRange values with an exclusive upper bound.
    For instance, ['2025-11-01', '2025-11-02') means the range includes
    only November 1st, not the 2nd. When displaying these values (e.g. in forms),
    subtract one day from the upper limit to present an inclusive date range
    that matches user expectations.
    """

    __tablename__ = "highlight"

    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False)
    description: sa_orm.Mapped[str] = sa_orm.mapped_column("description", sa.Text, nullable=False)
    availability_datespan: sa_orm.Mapped[psycopg2.extras.DateRange] = sa_orm.mapped_column(
        postgresql.DATERANGE, nullable=False
    )
    highlight_datespan: sa_orm.Mapped[psycopg2.extras.DateRange] = sa_orm.mapped_column(
        postgresql.DATERANGE, nullable=False
    )
    mediation_uuid: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.Text, nullable=False, unique=True)
    highlight_requests: sa_orm.Mapped[list["HighlightRequest"]] = sa_orm.relationship(
        "HighlightRequest", foreign_keys="HighlightRequest.highlightId", back_populates="highlight"
    )
    criteria: sa_orm.Mapped[list["criteria_models.Criterion"]] = sa_orm.relationship(
        "Criterion", foreign_keys="Criterion.highlightId", back_populates="highlight"
    )

    __table_args__ = (
        sa.CheckConstraint('length("mediation_uuid") <= 100'),
        sa.CheckConstraint('length("description") <= 2000'),
        sa.Index(
            "ix_highlight_unaccent_name",
            sa.func.immutable_unaccent("name"),
            postgresql_using="gin",
            postgresql_ops={"description": "gin_trgm_ops"},
        ),
    )

    @property
    def is_available(self) -> bool:
        today = datetime.date.today()
        return self.availability_datespan.upper > today and self.availability_datespan.lower <= today

    @property
    def mediation_url(self) -> str:
        return f"{settings.OBJECT_STORAGE_URL}/highlights/{self.mediation_uuid}"


class HighlightRequest(PcObject, Model):
    __tablename__ = "highlight_request"

    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id"), index=True, nullable=False
    )
    offer: sa_orm.Mapped["offers_models.Offer"] = sa_orm.relationship(
        "Offer", foreign_keys=[offerId], back_populates="highlight_requests"
    )

    highlightId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("highlight.id"), index=True, nullable=False
    )
    highlight: sa_orm.Mapped["Highlight"] = sa_orm.relationship(
        "Highlight", foreign_keys=[highlightId], back_populates="highlight_requests"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "highlightId",
            "offerId",
            name="unique_highlight_request_per_offer",
        ),
    )
