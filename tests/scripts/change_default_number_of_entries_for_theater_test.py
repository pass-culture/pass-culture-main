from models import AllocineVenueProvider, VenueSQLEntity
from repository import repository
from scripts.change_default_number_of_entries_for_theater import change_quantity_for_allocine_venue_provider
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue, create_offerer, create_provider, \
    create_allocine_venue_provider


@clean_database
def test_should_update_allocine_venue_provider_with_given_quantity(app):
    # Given
    provider = create_provider()
    offerer = create_offerer('123456789')
    venue = create_venue(offerer, siret='12345678912345')
    allocine_venue_provider = create_allocine_venue_provider(venue, provider, quantity=None)
    repository.save(allocine_venue_provider)

    # When
    change_quantity_for_allocine_venue_provider('12345678912345', 5)

    # Then
    allocine_venue_provider = AllocineVenueProvider.query.join(VenueSQLEntity).filter_by(siret='12345678912345').one()
    assert allocine_venue_provider.quantity == 5
