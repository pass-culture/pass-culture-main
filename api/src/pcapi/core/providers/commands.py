import logging

from pcapi.utils.blueprint import Blueprint

from . import models
from . import tasks


blueprint = Blueprint(__name__, __name__)
logger = logging.getLogger(__name__)


@blueprint.cli.command("synchronize_venue_providers_apis")
def synchronize_venue_providers_apis() -> None:
    providers_apis = models.Provider.query.filter(
        models.Provider.isActive == True, models.Provider.apiUrl != None
    ).all()
    for provider in providers_apis:
        venue_provider_ids = [
            id_
            for id_, in models.VenueProvider.query.filter_by(providerId=provider.id)
            .with_entities(models.VenueProvider.id)
            .all()
        ]
        tasks.synchronize_venue_providers_task.delay(venue_provider_ids)
