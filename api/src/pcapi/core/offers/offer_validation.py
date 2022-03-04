from dataclasses import dataclass
from typing import Union

from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.models.pc_object import PcObject
from pcapi.utils.custom_logic import OPERATIONS


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
        if all(item.resolve() for item in self.offer_validation_items):
            return self.factor
        return 1.0


def parse_offer_validation_config(
    offer: Union[CollectiveOffer, Offer], config: OfferValidationConfig
) -> tuple[float, list[OfferValidationRuleItem]]:
    minimum_score = float(config.specs["minimum_score"])
    rules = config.specs["rules"]

    rule_items = []
    for rule in rules:
        validation_items = []
        for parameter in rule["conditions"]:
            model = offer
            if parameter["model"] == "Venue":
                model = offer.venue
            elif parameter["model"] == "Offerer":
                model = offer.venue.managingOfferer

            validation_item = OfferValidationItem(
                model=model,
                attribute=parameter["attribute"],
                type=parameter.get("type"),
                condition=parameter["condition"],
            )
            validation_items.append(validation_item)
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
