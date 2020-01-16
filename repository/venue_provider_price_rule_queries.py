from _pydecimal import Decimal

from local_providers.price_rule import PriceRule
from models import VenueProvider, VenueProviderPriceRule


def save_venue_provider_price_rule(venue_provider: VenueProvider, price: Decimal):
    venue_provider_price_rule = VenueProviderPriceRule()
    venue_provider_price_rule.venueProvider = venue_provider
    venue_provider_price_rule.priceRule = PriceRule.default
    venue_provider_price_rule.price = price
    Repository.save(venue_provider_price_rule)
