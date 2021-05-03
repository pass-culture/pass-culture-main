from dataclasses import dataclass

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferValidationConfig
from pcapi.models import PcObject
from pcapi.utils.custom_logic import OPERATIONS


@dataclass
class OfferValidationItem:
    model: PcObject
    attribute: str
    type: list
    condition: dict
    factor: float

    def resolve(self) -> float:
        target_attribute = getattr(self.model, self.attribute)
        if OPERATIONS[self.condition["operator"]](target_attribute, self.condition["comparated"]):  # type: ignore[operator]
            return self.factor
        return 1.0


def parse_offer_validation_config(
    offer: Offer, config: OfferValidationConfig
) -> tuple[float, list[OfferValidationItem]]:
    minimum_score = float(config.specs.pop("minimum_score"))
    parameters = config.specs.pop("parameters")
    validation_items = []
    for _, parameter in parameters.items():
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
            factor=parameter["factor"],
        )
        validation_items.append(validation_item)
    return minimum_score, validation_items


def compute_offer_validation_score(validation_items: list[OfferValidationItem]) -> float:
    score = 1.0
    for validation_item in validation_items:
        score *= validation_item.resolve()
    return score
