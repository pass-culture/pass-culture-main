import sqlalchemy as sa

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Base, Model):
    name: str = sa.Column(sa.String(140), nullable=False, unique=True)
    description = sa.Column(sa.Text, nullable=True)
    startDateTime = sa.Column(sa.DateTime, nullable=True)
    endDateTime = sa.Column(sa.DateTime, nullable=True)

    categories: list["CriterionCategory"] = sa.orm.relationship(
        "CriterionCategory", secondary="criterion_category_mapping"
    )

    def __str__(self) -> str:
        return self.name


class VenueCriterion(PcObject, Base, Model):
    venueId: int = sa.Column(sa.BigInteger, sa.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False)
    criterionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False, index=True
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "venueId",
            "criterionId",
            name="unique_venue_criterion",
        ),
    )


class OfferCriterion(PcObject, Base, Model):
    __table_name__ = "offer_criterion"
    offerId: int = sa.Column(sa.BigInteger, sa.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False)
    criterionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "offerId",
            "criterionId",
            name="unique_offer_criterion",
        ),
    )


class CriterionCategory(PcObject, Base, Model):
    """
    Criterion categories used for partners counting, reporting, etc.
    """

    __tablename__ = "criterion_category"

    label: str = sa.Column(sa.String(140), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.label


class CriterionCategoryMapping(PcObject, Base, Model):
    __tablename__ = "criterion_category_mapping"

    criterionId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )
    categoryId: int = sa.Column(
        sa.BigInteger, sa.ForeignKey("criterion_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sa.UniqueConstraint("criterionId", "categoryId", name="unique_criterion_category"),)
