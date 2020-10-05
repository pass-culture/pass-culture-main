from models import AllocineVenueProvider, VenueSQLEntity
from repository import repository
from scripts.change_default_number_of_entries_for_theater import change_quantity_for_allocine_venue_provider
import pytest
from tests.model_creators.generic_creators import create_venue, create_offerer, create_provider, \
    create_allocine_venue_provider


@pytest.mark.usefixtures("db_session")
def should_set_given_quantity_for_allocine_venue_provider_of_given_siret(app):
    # Given
    provider = create_provider()
    offerer = create_offerer()
    venue = create_venue(offerer)
    allocine_venue_provider = create_allocine_venue_provider(venue, provider, quantity=None)
    repository.save(allocine_venue_provider)

    # When
    new_quantity = 5
    change_quantity_for_allocine_venue_provider(venue.siret, new_quantity)

    # Then
    allocine_venue_provider = AllocineVenueProvider.query.join(VenueSQLEntity).filter_by(siret=venue.siret).one()
    assert allocine_venue_provider.quantity == new_quantity
