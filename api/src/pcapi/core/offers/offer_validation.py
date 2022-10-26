from dataclasses import dataclass

import pcapi.core.educational.models as educational_models
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import CollectiveOfferTemplate
import pcapi.core.offerers.models as offerers_models
from pcapi.core.offers.exceptions import UnapplicableModel
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.models.pc_object import PcObject
from pcapi.utils.custom_logic import OPERATIONS


OFFER_LIKE_MODELS = {
    "Offer",
    "CollectiveOffer",
    "CollectiveOfferTemplate",
}


@dataclass
class OfferValidationItem:
    model: PcObject
    attribute: str
    type: list[str]
    condition: dict

    def resolve(self) -> bool:
        target_attribute = getattr(self.model, self.attribute)
        return OPERATIONS[self.condition["operator"]](target_attribute, self.condition["comparated"])  # type: ignore[operator]


@dataclass
class OfferValidationRuleItem:
    name: str
    factor: float
    offer_validation_items: list[OfferValidationItem]

    def resolve(self) -> float:
        if self.offer_validation_items:
            if all(item.resolve() for item in self.offer_validation_items):
                return self.factor
        return 1.0


def _get_model(
    offer: CollectiveOffer | CollectiveOfferTemplate | Offer, parameter_model: str
) -> (
    Offer
    | CollectiveOffer
    | CollectiveOfferTemplate
    | educational_models.CollectiveStock
    | offerers_models.Venue
    | offerers_models.Offerer
):
    if parameter_model in OFFER_LIKE_MODELS and offer.__class__.__name__ == parameter_model:
        model = offer
    elif parameter_model == "CollectiveStock" and isinstance(offer, CollectiveOffer):
        model = offer.collectiveStock
    elif parameter_model == "Venue":
        model = offer.venue
    elif parameter_model == "Offerer":
        model = offer.venue.managingOfferer
    else:
        raise UnapplicableModel()
    return model


def parse_offer_validation_config(
    offer: CollectiveOffer | CollectiveOfferTemplate | Offer, config: OfferValidationConfig
) -> tuple[float, list[OfferValidationRuleItem]]:
    minimum_score = float(config.specs["minimum_score"])
    rules = config.specs["rules"]

    rule_items = []
    for rule in rules:
        validation_items = []
        for parameter in rule["conditions"]:
            try:
                model = _get_model(offer, parameter.get("model", None))
            except UnapplicableModel:
                break

            validation_item = OfferValidationItem(
                model=model,
                attribute=parameter["attribute"],
                type=parameter.get("type"),
                condition=parameter["condition"],
            )
            validation_items.append(validation_item)
        else:
            if validation_items:
                rule_item = OfferValidationRuleItem(
                    name=rule["name"], factor=rule["factor"], offer_validation_items=validation_items
                )
                rule_items.append(rule_item)
    return minimum_score, rule_items


def compute_offer_validation_score(validation_items: list[OfferValidationRuleItem]) -> float:
    score = 1.0
    for validation_item in validation_items:
        score *= validation_item.resolve()
        if score == 0:
            break
    return score
