import datetime
import typing

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from pcapi.core.criteria import constants
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


if typing.TYPE_CHECKING:
    from pcapi.core.highlights import models as highlights_models
    from pcapi.core.offerers.models import Venue
    from pcapi.core.offers.models import Offer


class CriterionCategoryMapping(PcObject, Model):
    __tablename__ = "criterion_category_mapping"

    criterionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )
    categoryId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("criterion_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("criterionId", "categoryId", name="unique_criterion_category"),)


class Criterion(PcObject, Model):
    __tablename__ = "criterion"
    name: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False, unique=True)
    description: sa_orm.Mapped[str | None] = sa_orm.mapped_column(sa.Text, nullable=True)
    startDateTime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)
    endDateTime: sa_orm.Mapped[datetime.datetime | None] = sa_orm.mapped_column(sa.DateTime, nullable=True)

    venue_criteria: sa_orm.Mapped[list["Venue"]] = sa_orm.relationship(
        "Venue", back_populates="criteria", lazy="dynamic", secondary="venue_criterion"
    )
    offers: sa_orm.Mapped[list["Offer"]] = sa_orm.relationship(
        "Offer", back_populates="criteria", lazy="dynamic", secondary="offer_criterion"
    )
    categories: sa_orm.Mapped[list["CriterionCategory"]] = sa_orm.relationship(
        "CriterionCategory", secondary=CriterionCategoryMapping.__table__
    )

    highlightId: sa_orm.Mapped[int | None] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("highlight.id", ondelete="SET NULL"), index=True, nullable=True
    )
    highlight: sa_orm.Mapped["highlights_models.Highlight"] = sa_orm.relationship(
        "Highlight", foreign_keys=[highlightId], back_populates="criteria"
    )

    def __str__(self) -> str:
        return self.name


class VenueCriterion(PcObject, Model):
    __tablename__ = "venue_criterion"
    venueId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "venueId",
            "criterionId",
            name="unique_venue_criterion",
        ),
    )


class OfferCriterion(PcObject, Model):
    __tablename__ = "offer_criterion"
    offerId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: sa_orm.Mapped[int] = sa_orm.mapped_column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "offerId",
            "criterionId",
            name="unique_offer_criterion",
        ),
    )


class CriterionCategory(PcObject, Model):
    """
    Criterion categories used for partners counting, reporting, etc.
    """

    __tablename__ = "criterion_category"

    label: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String(140), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.label

    @property
    def is_editable(self) -> bool:
        """
        For informational purposes only.
        The label field is not editable in the backoffice and should never be modified if its value is HIGHLIGHT_CATEGORY_LABEL.
        """
        return self.label != constants.HIGHLIGHT_CATEGORY_LABEL
