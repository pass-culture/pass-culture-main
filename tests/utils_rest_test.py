import pytest

from models import PcObject, Venue, ApiErrors
from tests.conftest import clean_database
from tests.test_utils import create_venue, create_offerer
from utils.human_ids import humanize
from utils.rest import load_or_raise_error


@pytest.mark.standalone
class TestLoadOrRaiseErrorTest:
    @clean_database
    def test_returns_object_if_found(self, app):
        # Given
        id = humanize(1)

        # When
        with pytest.raises(ApiErrors) as error:
            load_or_raise_error(Venue, id)

        assert error.value.errors['global'] == [
            'Aucun objet ne correspond à cet identifiant dans notre base de données']

    @clean_database
    def test_raises_api_error_if_no_object(self, app):
        # Given
        offerer = create_offerer()
        venue = create_venue(offerer)
        PcObject.check_and_save(venue)

        # When
        try:
            load_or_raise_error(Venue, humanize(venue.id))

        except:
            assert False