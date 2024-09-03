import datetime
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
from pcapi.scripts.provider_migration.data import VENUES_TO_MIGRATE_BY_DATE_AND_HOUR


logger = logging.getLogger(__name__)


def _delete_venue_provider(
    venue_provider: providers_models.VenueProvider,
    author: users_models.User,
    comment: str,
) -> None:
    venue_id = venue_provider.venueId
    provider_id = venue_provider.provider.id
    history_api.add_action(
        history_models.ActionType.LINK_VENUE_PROVIDER_DELETED,
        author=author,
        venue=venue_provider.venue,
        provider_id=venue_provider.providerId,
        provider_name=venue_provider.provider.name,
        comment=comment,
    )
    db.session.delete(venue_provider)
    logger.info(
        "Deleted VenueProvider for venue %d",
        venue_id,
        extra={"venue_id": venue_id, "provider_id": provider_id},
        technical_message_id="offer.sync.deleted",
    )


def _migrate_venue_providers(
    provider_id: int,
    venues_ids: list[int],
    migration_author_id: int,
    comment: str,
) -> None:
    """
    For each venue :
        1. Delete existing VenueProviders
        2. Insert new VenueProvider (for given provider)
    """
    provider = providers_models.Provider.query.get(provider_id)

    if not provider:
        logger.info(f"No provider was found for id {provider_id}")  # pylint: disable=logging-fstring-interpolation
        return

    venues = (
        offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(venues_ids))
        .options(joinedload(offerers_models.Venue.venueProviders))
        .all()
    )

    if len(venues) != len(venues_ids):
        found_venues_ids = [venue.id for venue in venues]
        logger.info(  # pylint: disable=logging-fstring-interpolation
            f"Some venues don't exist {[id for id in venues_ids if id not in found_venues_ids]}"
        )
        return

    user = users_models.User.query.get(migration_author_id)

    with transaction():
        for venue in venues:
            logger.info(f"Handling venue <#{venue.id} - {venue.name}>")  # pylint: disable=logging-fstring-interpolation
            if len(venue.venueProviders):
                for venue_provider in venue.venueProviders:
                    _delete_venue_provider(venue_provider, author=user, comment=comment)
            providers_api.create_venue_provider(provider.id, venue.id, current_user=user)


def execute_scheduled_venue_provider_migration() -> None:
    now = datetime.datetime.utcnow()
    today = now.strftime("%d/%m/%y")
    current_hour = now.hour
    venues_to_migrate_today = VENUES_TO_MIGRATE_BY_DATE_AND_HOUR.get(today)

    if not venues_to_migrate_today:
        logger.info("No venues to migrate today")
        return

    if current_hour < 8:  # i.e. < 10h in Paris Tz
        migration_data = venues_to_migrate_today.get("10H")
    else:
        migration_data = venues_to_migrate_today.get("14H")

    if not migration_data:
        logger.info("No venues to migrate at this time of day")
        return

    provider_id = migration_data["target_provider_id"]
    comment = migration_data["comment"]
    venues_ids = migration_data["venues_ids"]

    _migrate_venue_providers(
        provider_id=provider_id,  # type: ignore[arg-type]
        venues_ids=venues_ids,  # type: ignore[arg-type]
        migration_author_id=2568200,  # id of our backend tech lead user
        comment=comment,  # type: ignore[arg-type]
    )


if __name__ == "__main__":
    app.app_context().push()
    execute_scheduled_venue_provider_migration()
