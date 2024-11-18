import sqlalchemy as sqla

from pcapi.core.offerers.base_models import Venue
from pcapi.core.offers.models import Offer
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


VenueCriterion = sqla.Table(
    "venue_criterion",
    Base.metadata,
    sqla.Column("venueId", sqla.ForeignKey(Venue.id, ondelete="CASCADE"), index=True, nullable=False),
    sqla.Column("criterionId", sqla.ForeignKey(Criterion.id, ondelete="CASCADE"), nullable=False, index=True),
    sqla.UniqueConstraint("venueId", "criterionId", name="unique_venue_criterion"),
)


OfferCriterion = sqla.Table(
    "offer_criterion",
    Base.metadata,
    sqla.Column("offerId", sqla.ForeignKey(Offer.id, ondelete="CASCADE"), index=True, nullable=False),
    sqla.Column("criterionId", sqla.ForeignKey(Criterion.id, ondelete="CASCADE"), index=True, nullable=False),
    sqla.UniqueConstraint("offerId", "criterionId", name="unique_offer_criterion"),
)


class CriterionCategory(PcObject, Base, Model):
    """
    Criterion categories used for partners counting, reporting, etc.
    """

    __tablename__ = "criterion_category"

    label: str = sqla.Column(sqla.String(140), nullable=False, unique=True)

    def __str__(self) -> str:
        return self.label


CriterionCategoryMapping = sqla.Table(
    "criterion_category_mapping",
    Base.metadata,
    sqla.Column("criterionId", sqla.ForeignKey(Criterion.id, ondelete="CASCADE"), index=True, nullable=False),
    sqla.Column("categoryId", sqla.ForeignKey(CriterionCategory.id, ondelete="CASCADE"), index=True, nullable=False),
    sqla.UniqueConstraint("criterionId", "categoryId", name="unique_criterion_category"),
)
