from decimal import Decimal
import logging

from pcapi.core.offerers.models import Venue
from pcapi.core.providers.models import AllocineVenueProvider
from pcapi.core.providers.models import AllocineVenueProviderPriceRule
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def modify_allocine_price_rule_for_venue_by_id(venue_id: int, new_price: Decimal) -> None:
    logger.info("Venue %s priceRule to be updated, new price: %s", venue_id, new_price)
    allocine_venue_provider = AllocineVenueProvider.query.filter_by(venueId=venue_id).one_or_none()
    if allocine_venue_provider is not None:
        _modify_allocine_price_rule_for_venue(allocine_venue_provider, new_price)
    else:
        logger.info("This venue is not yet synchronized with Allocine")


def modify_allocine_price_rule_for_venue_by_siret(venue_siret: str, new_price: Decimal) -> None:
    logger.info("Venue %s priceRule to be updated, new price: %s", venue_siret, new_price)
    allocine_venue_provider = AllocineVenueProvider.query.join(Venue).filter_by(siret=venue_siret).one_or_none()
    if allocine_venue_provider is not None:
        _modify_allocine_price_rule_for_venue(allocine_venue_provider, new_price)
    else:
        logger.info("This venue is not yet synchronized with Allocine")


def _modify_allocine_price_rule_for_venue(allocine_venue_provider: AllocineVenueProvider, new_price: Decimal) -> None:
    venue_provider_price_rule = AllocineVenueProviderPriceRule.query.filter_by(
        allocineVenueProviderId=allocine_venue_provider.id
    ).one_or_none()
    if venue_provider_price_rule is not None:
        venue_provider_price_rule.price = new_price
        repository.save(venue_provider_price_rule)
        logger.info("Venue priceRule updated")
