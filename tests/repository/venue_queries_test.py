from repository import repository
from repository.venue_queries import find_by_managing_offerer_id_and_siret
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue


class FindByManagingOffererIdAndSiretTest:
    @clean_database
    def test_return_none_when_not_matching_venues(self):
        # Given
        offerer = create_offerer()
        not_matching_venue = create_venue(offerer, siret='12345678988888')
        repository.save(not_matching_venue)

        # When
        venue = find_by_managing_offerer_id_and_siret(
            offerer.id, '12345678912345')

        # Then
        assert venue is None

    @clean_database
    def test_return_matching_venue(self):
        # Given
        offerer = create_offerer()
        matching_venue = create_venue(offerer, siret='12345678912345')
        repository.save(matching_venue)

        # When
        venue = find_by_managing_offerer_id_and_siret(
            offerer.id, '12345678912345')

        # Then
        assert venue.id == matching_venue.id
        assert venue.siret == '12345678912345'
        assert venue.managingOffererId == offerer.id
