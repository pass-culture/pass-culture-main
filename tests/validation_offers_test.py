import pytest

from models import ApiErrors
from validation.offers import check_has_venue_id


@pytest.mark.standalone
class CheckHasVenueIdTest:
    def test_raises_exception_when_venue_id_is_None(self):
        # Given
        venue_id = None

        # When
        with pytest.raises(ApiErrors) as error:
            check_has_venue_id(venue_id)

        assert error.value.errors['venueId'] == ['Vous devez préciser un identifiant de lieu']

    def test_raises_does_not_raise_exception_when_venue_id(self):
        # Given
        venue_id = 'AE'

        # When
        try:
            check_has_venue_id(venue_id)
        except:
            assert False
