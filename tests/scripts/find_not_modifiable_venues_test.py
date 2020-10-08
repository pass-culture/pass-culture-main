from pcapi.repository import repository
from pcapi.scripts.find_not_modifiable_venues import generate_non_editable_venues_csv, _get_non_editable_venues
import pytest
from pcapi.model_creators.generic_creators import create_venue, create_offerer


class GetNonEditableVenuesTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_return_offerer_has_no_name(self, app):
        # given
        offerer = create_offerer(name='')
        venue = create_venue(offerer)
        offerer_2 = create_offerer(siren='123456788')
        venue_2 = create_venue(offerer_2, siret='12345678899999')

        repository.save(venue, venue_2)

        # when
        venues = _get_non_editable_venues()

        # then
        assert len(venues) == 1
        editable_venue = venues[0]
        assert editable_venue.venueId == venue.id

    @pytest.mark.usefixtures("db_session")
    def test_should_return_venue_when_siret_does_not_match_offerer_siren(self, app):
        # given
        offerer = create_offerer(siren='123456788')
        venue = create_venue(offerer, siret='88345678899999')
        offerer_2 = create_offerer(siren='199999988')
        venue_2 = create_venue(offerer_2, siret='19999998899999')

        repository.save(venue, venue_2)

        # when
        venues = _get_non_editable_venues()

        # then
        assert len(venues) == 1
        editable_venue = venues[0]
        assert editable_venue.venueId == venue.id

    @pytest.mark.usefixtures("db_session")
    def test_should_return_venue_when_offerer_siren_is_none(self, app):
        # given
        offerer = create_offerer(siren=None)
        venue = create_venue(offerer, siret='88345678899999')
        offerer_2 = create_offerer(siren='199999988')
        venue_2 = create_venue(offerer_2, siret='19999998899999')
        repository.save(venue, venue_2)

        # when
        venues = _get_non_editable_venues()

        # then
        assert len(venues) == 1
        editable_venue = venues[0]
        assert editable_venue.venueId == venue.id

    @pytest.mark.usefixtures("db_session")
    def test_should_return_venue_when_siret_is_none_and_offerer_siren_is_none(self, app):
        # given
        offerer = create_offerer(siren=None)
        venue = create_venue(offerer, siret=None, comment='comment')
        offerer_2 = create_offerer(siren='199999988')
        venue_2 = create_venue(offerer_2, siret='19999998899999')

        repository.save(venue, venue_2)

        # when
        venues = _get_non_editable_venues()

        # then
        assert len(venues) == 1
        editable_venue = venues[0]
        assert editable_venue.venueId == venue.id


class GenerateNonEditableVenuesCsv:
    @pytest.mark.usefixtures("db_session")
    def test_should_generate_non_editable_venues_csv_with_correct_header_and_correct_informations(self, app):
        # given
        offerer = create_offerer(siren='123456788')
        venue = create_venue(offerer, siret='88345678899999')

        repository.save(venue)

        # when
        csv = generate_non_editable_venues_csv()

        # Then
        csv_as_lines = csv.splitlines()

        assert csv_as_lines[0] == 'offerer_id,offerer_humanized_id,offerer_siren,offerer_name,venue_id,venue_humanized_id,venue_siret,venue_name,venue_departement'
        assert csv_as_lines[1] == '9,BE,123456788,Test Offerer,9,BE,88345678899999,La petite librairie,93'