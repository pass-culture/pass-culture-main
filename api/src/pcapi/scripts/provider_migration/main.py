import logging

from sqlalchemy.orm import joinedload

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.providers import api as providers_api
from pcapi.core.providers import models as providers_models
from pcapi.core.users import models as users_models
from pcapi.flask_app import app
from pcapi.models import db
from pcapi.repository import transaction
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job


logger = logging.getLogger(__name__)


def delete_venue_provider(venue_provider: providers_models.VenueProvider, author: users_models.User) -> None:
    update_venue_synchronized_offers_active_status_job.delay(venue_provider.venueId, venue_provider.providerId, False)
    venue_id = venue_provider.venueId
    provider_id = venue_provider.provider.id
    history_api.add_action(
        history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
        author,
        venue=venue_provider.venue,
        provider_id=venue_provider.providerId,
        provider_name=venue_provider.provider.name,
        comment="(PC-30523) Update Gibert Joseph VenueProvider for new API usage.",
    )
    db.session.delete(venue_provider)
    logger.info(
        "Deleted VenueProvider for venue %d",
        venue_id,
        extra={"venue_id": venue_id, "provider_id": provider_id},
        technical_message_id="offer.sync.deleted",
    )


def edit_venue_provider(provider_id: int, venue_ids: list[int], user_email: str) -> None:
    """
    For each venue:
    1. Delete existing VenueProviders
    2. Insert new VenueProvider (for given provider)
    """
    provider = providers_models.Provider.query.get(provider_id)
    if not provider:
        logger.info(f"No provider was found for id {provider_id}")  # pylint: disable=logging-fstring-interpolation
        return

    venues = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(venue_ids))
        .options(joinedload(offerers_models.Venue.venueProviders))
        .all()
    )
    if len(venues) != len(venue_ids):
        found_venues_ids = [venue.id for venue in venues]
        logger.info(  # pylint: disable=logging-fstring-interpolation
            f"Some venues don't exist {[id for id in venue_ids if id not in found_venues_ids]}"
        )
        return

    user = users_models.User.query.filter_by(email=user_email).one_or_none()
    if not user:
        logger.info(f"User {user_email} don't exist")  # pylint: disable=logging-fstring-interpolation

    with transaction():
        for venue in venues:
            logger.info(f"Handling venue <#{venue.id} - {venue.name}>")  # pylint: disable=logging-fstring-interpolation
            if len(venue.venueProviders):
                for venue_provider in venue.venueProviders:
                    delete_venue_provider(venue_provider, user)
            providers_api.create_venue_provider(provider.id, venue.id)


if __name__ == "__main__":
    app.app_context().push()
    edit_venue_provider(
        2110,  # Provider: NUSSEO
        [  # Venues: Gibert Joseph venues
            18081,
            17724,
            17723,
            17721,
            17725,
            17726,
            17820,
            17874,
            17825,
            17826,
            17827,
            17828,
            17829,
            14929,
            17836,
            17839,
            17840,
            17842,
            17718,
            17719,
            17680,
            17844,
            17845,
            49517,
        ],
        "matthieu.geoffray@passculture.app",
    )
