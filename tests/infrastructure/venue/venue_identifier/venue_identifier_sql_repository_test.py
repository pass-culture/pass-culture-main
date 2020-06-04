from domain.venue.venue_identifier.venue_identifier import VenueIdentifier
from infrastructure.repository.venue.venue_identifier import venue_identifier_domain_converter
from infrastructure.repository.venue.venue_identifier.venue_identifier_sql_repository import \
    VenueIdentifierSQLRepository
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue


class VenueIdentifierSQLRepositoryTest:
    def setup_method(self) -> None:
        self.venue_sql_repository = VenueIdentifierSQLRepository()

    @clean_database
    def test_returns_a_venue_when_venue_with_siret_is_found(self, app: object) -> None:
        # given
        siret = "12345678912345"
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, siret=siret)

        repository.save(venue)

        expected_venue = venue_identifier_domain_converter.to_domain(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_siret(siret)

        # then
        assert isinstance(found_venue, VenueIdentifier)
        assert found_venue.siret == expected_venue.siret
        assert found_venue.id == expected_venue.id

    @clean_database
    def test_should_return_none_when_no_venue_with_siret_was_found(self, app: object) -> None:
        # given
        siret = "12345678912345"
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, siret=siret)
        repository.save(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_siret(siret="98765432112345")

        # then
        assert found_venue is None

    @clean_database
    def test_returns_a_venue_when_venue_with_name_is_found(self, app: object) -> None:
        # given
        name = 'VENUE NAME'
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, name=name, comment='a comment', siret=None)

        repository.save(venue)

        expected_venue = venue_identifier_domain_converter.to_domain(venue)

        # when
        found_venues = self.venue_sql_repository.find_by_name(name, offerer.id)

        # then
        assert len(found_venues) == 1
        found_venue = found_venues[0]
        assert isinstance(found_venue, VenueIdentifier)
        assert found_venue.name == expected_venue.name
        assert found_venue.id == expected_venue.id
        assert found_venue.siret is None

    @clean_database
    def test_should_return_none_when_venue_with_name_was_found_but_in_another_offerer(self, app: object) -> None:
        # given
        name = 'Venue name'
        offerer = create_offerer()
        other_offerer = create_offerer(siren='123456798')
        venue = create_venue(offerer=other_offerer, name=name, siret=None, comment='a comment')
        repository.save(venue, other_offerer)

        # when
        found_venue = self.venue_sql_repository.find_by_name(name, offerer.id)

        # then
        assert found_venue == []

    @clean_database
    def test_should_return_none_when_no_venue_with_name_was_found(self, app: object) -> None:
        # given
        name = 'Venue name'
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, name=name, siret=None, comment='a comment')
        repository.save(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_name('some other name', offerer.id)

        # then
        assert found_venue == []
