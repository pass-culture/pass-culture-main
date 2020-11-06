from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from pcapi.models import Offer


class EligibilityRule(ABC):
    @abstractmethod
    def apply(self, offer: Offer, offer_details: dict):
        pass


class NameHasChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        offer_name = offer.name
        indexed_offer_name = offer_details['name']

        return offer_name != indexed_offer_name


class DatesHaveChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        if not offer.isEvent:
            return False

        offer_dates = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), offer.activeStocks))
        indexed_offer_dates = offer_details['dates']

        return offer_dates != indexed_offer_dates


class PricesHaveChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        offer_prices = list(map(lambda stock: float(stock.price), offer.activeStocks))
        indexed_offer_prices = offer_details['prices']

        return offer_prices != indexed_offer_prices


class EligibilityRules(Enum):
    NAME_HAS_CHANGED = NameHasChanged()
    DATES_HAVE_CHANGED = DatesHaveChanged()
    PRICES_HAVE_CHANGED = PricesHaveChanged()
