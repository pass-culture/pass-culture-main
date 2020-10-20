from decimal import Decimal

from pcapi.models import AllocineVenueProvider, AllocineVenueProviderPriceRule, VenueSQLEntity
from pcapi.repository import repository
from pcapi.utils.logger import logger


def modify_allocine_price_rule_for_venue_by_id(venue_id: int, new_price: Decimal) -> None:
    logger.info(f"Venue {venue_id} priceRule to be updated, new price: {new_price}")
    allocine_venue_provider = AllocineVenueProvider.query.filter_by(venueId=venue_id).one_or_none()
    if allocine_venue_provider is not None:
        _modify_allocine_price_rule_for_venue(allocine_venue_provider, new_price)
    else:
        logger.info("This venue is not yet synchronized with Allocine")


def modify_allocine_price_rule_for_venue_by_siret(venue_siret: str, new_price: Decimal) -> None:
    logger.info(f"Venue {venue_siret} priceRule to be updated, new price: {new_price}")
    allocine_venue_provider = AllocineVenueProvider.query.join(VenueSQLEntity).filter_by(siret=venue_siret).one_or_none()
    if allocine_venue_provider is not None:
        _modify_allocine_price_rule_for_venue(allocine_venue_provider, new_price)
    else:
        logger.info("This venue is not yet synchronized with Allocine")


def _modify_allocine_price_rule_for_venue(allocine_venue_provider: AllocineVenueProvider, new_price: Decimal) -> None:
    venue_provider_price_rule = AllocineVenueProviderPriceRule.query.filter_by(allocineVenueProviderId=allocine_venue_provider.id).one_or_none()
    if venue_provider_price_rule is not None:
        venue_provider_price_rule.price = new_price
        repository.save(venue_provider_price_rule)
        logger.info("Venue priceRule updated")
