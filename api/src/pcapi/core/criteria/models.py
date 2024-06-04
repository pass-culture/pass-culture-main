import sqlalchemy as sqla

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.pc_object import PcObject


class Criterion(PcObject, Base, Model):
    name: str = sqla.Column(sqla.String(140), nullable=False, unique=True)
    description = sqla.Column(sqla.Text, nullable=True)
    startDateTime = sqla.Column(sqla.DateTime, nullable=True)
    endDateTime = sqla.Column(sqla.DateTime, nullable=True)

    categories: list["CriterionCategory"] = sqla.orm.relationship(
        "CriterionCategory", secondary="criterion_category_mapping"
    )

    def __str__(self) -> str:
        return self.name


class VenueCriterion(PcObject, Base, Model):
    venueId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("venue.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), nullable=False, index=True
    )

    __table_args__ = (
        sqla.UniqueConstraint(
            "venueId",
            "criterionId",
            name="unique_venue_criterion",
        ),
    )


class OfferCriterion(PcObject, Base, Model):
    __table_name__ = "offer_criterion"
    offerId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("offer.id", ondelete="CASCADE"), index=True, nullable=False
    )
    criterionId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (
        sqla.UniqueConstraint(
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

    label: str = sqla.Column(sqla.String(140), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.label


class CriterionCategoryMapping(PcObject, Base, Model):
    __tablename__ = "criterion_category_mapping"

    criterionId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion.id", ondelete="CASCADE"), index=True, nullable=False
    )
    categoryId: int = sqla.Column(
        sqla.BigInteger, sqla.ForeignKey("criterion_category.id", ondelete="CASCADE"), index=True, nullable=False
    )

    __table_args__ = (sqla.UniqueConstraint("criterionId", "categoryId", name="unique_criterion_category"),)
