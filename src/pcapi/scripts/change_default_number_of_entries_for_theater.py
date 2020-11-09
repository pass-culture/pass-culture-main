from pcapi.models import AllocineVenueProvider
from pcapi.models import VenueSQLEntity
from pcapi.repository import repository


def change_quantity_for_allocine_venue_provider(siret: str, quantity: int):
    allocine_venue_provider = AllocineVenueProvider.query.join(VenueSQLEntity).filter_by(siret=siret).one()
    allocine_venue_provider.quantity = quantity
    repository.save(allocine_venue_provider)
