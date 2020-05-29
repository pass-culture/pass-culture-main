from domain.venue.venue import Venue
from infrastructure.repository.venue import venue_domain_converter
from infrastructure.repository.venue.venue_sql_repository import VenueSQLRepository
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_user, create_user_offerer


class VenueSQLRepositoryTest:
    def setup_method(self):
        self.venue_sql_repository = VenueSQLRepository()

    @clean_database
    def test_returns_a_venue_when_venue_with_siret_is_found(self, app):
        # given
        siret = "12345678912345"
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, siret=siret)

        repository.save(venue)

        expected_venue = venue_domain_converter.to_domain(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_siret(siret)

        # then
        assert isinstance(found_venue, Venue)
        assert found_venue.siret == expected_venue.siret
        assert found_venue.id == expected_venue.id

    @clean_database
    def test_should_return_none_when_no_venue_with_siret_was_found(self, app):
        # given
        siret = "12345678912345"
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, siret=siret)
        repository.save(venue)

        expected_venue = venue_domain_converter.to_domain(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_siret(siret="98765432112345")

        # then
        assert found_venue is None

    @clean_database
    def test_returns_a_venue_when_venue_with_name_is_found(self, app):
        # given
        name = 'VENUE NAME'
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, name=name, comment='a comment', siret=None)

        repository.save(venue)

        expected_venue = venue_domain_converter.to_domain(venue)

        # when
        found_venues = self.venue_sql_repository.find_by_name(name, offerer.id)

        # then
        assert len(found_venues) == 1
        found_venue = found_venues[0]
        assert isinstance(found_venue, Venue)
        assert found_venue.name == expected_venue.name
        assert found_venue.id == expected_venue.id
        assert found_venue.siret is None

    @clean_database
    def test_should_return_none_when_venue_with_name_was_found_but_in_another_offerer(self, app):
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
    def test_should_return_none_when_no_venue_with_name_was_found(self, app):
        # given
        name = 'Venue name'
        offerer = create_offerer()
        venue = create_venue(offerer=offerer, name=name, siret=None, comment='a comment')
        repository.save(venue)

        # when
        found_venue = self.venue_sql_repository.find_by_name('some other name', offerer.id)

        # then
        assert found_venue == []


class GetAllByProIdentifierTest:
    def setup_method(self):
        self.venue_sql_repository = VenueSQLRepository()

    @clean_database
    def test_returns_all_venues_of_pro_user(self, app):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        create_user_offerer(user=pro_user, offerer=offerer)
        venue_1 = create_venue(offerer=offerer, siret='12345678912345')
        venue_2 = create_venue(offerer=offerer, siret='98765432198765')

        repository.save(venue_1, venue_2)

        expected_venue_1 = venue_domain_converter.to_domain(venue_1)
        expected_venue_2 = venue_domain_converter.to_domain(venue_2)

        # when
        found_venues = self.venue_sql_repository.get_all_by_pro_identifier(pro_user.id)

        # then
        assert len(found_venues) == 2
        assert isinstance(found_venues[0], Venue)
        found_venues_id = [venue.id for venue in found_venues]
        assert set(found_venues_id) == {expected_venue_1.id, expected_venue_2.id}

    @clean_database
    def test_returns_empty_list_when_no_venues_exist(self, app):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        user_offerer = create_user_offerer(user=pro_user, offerer=offerer)
        repository.save(user_offerer)

        # when
        found_venues = self.venue_sql_repository.get_all_by_pro_identifier(pro_user.id)

        # then
        assert found_venues == []

    @clean_database
    def test_returns_all_venues_of_pro_user_ordered_by_name(self, app):
        # given
        pro_user = create_user()
        offerer = create_offerer()
        create_user_offerer(user=pro_user, offerer=offerer)
        venue_1 = create_venue(offerer=offerer, siret='12345678912345', name='B')
        venue_2 = create_venue(offerer=offerer, siret='98765432198765', name='A')

        repository.save(venue_1, venue_2)

        expected_venue_1 = venue_domain_converter.to_domain(venue_1)
        expected_venue_2 = venue_domain_converter.to_domain(venue_2)

        # when
        found_venues = self.venue_sql_repository.get_all_by_pro_identifier(pro_user.id)

        # then
        assert len(found_venues) == 2
        assert found_venues[0].name == expected_venue_2.name
        assert found_venues[1].name == expected_venue_1.name
