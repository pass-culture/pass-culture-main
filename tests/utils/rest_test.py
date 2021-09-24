import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.models import ApiErrors
from pcapi.models import Venue
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize
from pcapi.utils.rest import load_or_raise_error


class TestLoadOrRaiseErrorTest:
    @pytest.mark.usefixtures("db_session")
    def test_returns_object_if_found(self, app):
        # When
        with pytest.raises(ApiErrors) as error:
            load_or_raise_error(Venue, humanize(1))

        assert error.value.errors["global"] == [
            "Aucun objet ne correspond à cet identifiant dans notre base de données"
        ]

    @pytest.mark.usefixtures("db_session")
    def test_raises_api_error_if_no_object(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        repository.save(venue)

        # Then the following should not raise
        load_or_raise_error(Venue, humanize(venue.id))
