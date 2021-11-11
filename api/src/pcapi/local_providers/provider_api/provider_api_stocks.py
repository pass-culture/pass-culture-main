import logging

from sqlalchemy.orm.util import aliased

import pcapi.connectors.notion as notion_connector
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.models import db

from . import synchronize_provider_api


logger = logging.getLogger(__name__)


def synchronize_stocks() -> None:
    # Alias for provider table, and explicit "on" clause for the "join", are mandatory because
    # VenueProvider model already has a "select" on the provider table for its polymorphic query
    provider_alias = aliased(Provider)

    venue_providers = (
        VenueProvider.query.join(provider_alias, provider_alias.id == VenueProvider.providerId)
        .filter(provider_alias.apiUrl.isnot(None))
        .filter(provider_alias.isActive.is_(True))
        .filter(VenueProvider.isActive.is_(True))
        .all()
    )

    for venue_provider in venue_providers:
        # We need to stock these values inside variables to prevent a crash
        # if the session is broken and we need to log them
        venue_id = venue_provider.venueId
        venue_provider_id = venue_provider.id
        venue_id_at_offer_provider = venue_provider.venueIdAtOfferProvider
        provider_name = venue_provider.provider.name

        try:
            synchronize_provider_api.synchronize_venue_provider(venue_provider)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Could not synchronize venue_provider=%s: %s", venue_provider_id, exc)
            notion_connector.add_to_synchronization_error_database(
                exception=exc,
                provider_name=provider_name,
                venue_id=venue_id,
                venue_id_at_offer_provider=venue_id_at_offer_provider,
            )
            db.session.rollback()
