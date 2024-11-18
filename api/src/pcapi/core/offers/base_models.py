import sqlalchemy as sa

from pcapi.models import Base
from pcapi.models import Model
from pcapi.models.deactivable_mixin import DeactivableMixin
from pcapi.models.pc_object import PcObject


class OfferValidationRule(PcObject, Base, Model, DeactivableMixin):
    __tablename__ = "offer_validation_rule"
    name: str = sa.Column(sa.Text, nullable=False)
    offers: list["Offer"] = sa.orm.relationship(
        "Offer", secondary="validation_rule_offer_link", back_populates="flaggingValidationRules"
    )
    collectiveOffers: list["CollectiveOffer"] = sa.orm.relationship(
        "CollectiveOffer", secondary="validation_rule_collective_offer_link", back_populates="flaggingValidationRules"
    )
    collectiveOfferTemplates: list["CollectiveOfferTemplate"] = sa.orm.relationship(
        "CollectiveOfferTemplate",
        secondary="validation_rule_collective_offer_template_link",
        back_populates="flaggingValidationRules",
    )
