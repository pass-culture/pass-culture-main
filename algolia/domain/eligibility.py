from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

from models import Offer


class EligibilityRule(ABC):
    @abstractmethod
    def apply(self, offer: Offer, offer_details: dict):
        pass


class NameHasChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        offer_name = offer.name
        indexed_offer_name = offer_details['name']

        return offer_name != indexed_offer_name


class DateRangeHasChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        offer_date_range = list(map(str, offer.dateRange.datetimes))
        indexed_offer_date_range = offer_details['dateRange']

        return offer_date_range != indexed_offer_date_range


class DatesHaveChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        if not offer.isEvent:
            return False

        offer_dates = list(map(lambda stock: datetime.timestamp(stock.beginningDatetime), offer.notDeletedStocks))
        indexed_offer_dates = offer_details['dates']

        return offer_dates != indexed_offer_dates


class PricesHaveChanged(EligibilityRule):
    def apply(self, offer: Offer, offer_details: dict):
        offer_prices = list(map(lambda stock: float(stock.price), offer.notDeletedStocks))
        indexed_offer_prices = offer_details['prices']

        return offer_prices != indexed_offer_prices


class EligibilityRules(Enum):
    NAME_HAS_CHANGED = NameHasChanged()
    DATE_RANGE_HAS_CHANGED = DateRangeHasChanged()
    DATES_HAVE_CHANGED = DatesHaveChanged()
    PRICES_HAVE_CHANGED = PricesHaveChanged()
