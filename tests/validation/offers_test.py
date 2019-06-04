import pytest

from models import ApiErrors, ThingType, EventType
from validation.offers import check_has_venue_id, check_offer_type_is_valid


class CheckHasVenueIdTest:
    def test_raises_exception_when_venue_id_is_None(self):
        # Given
        venue_id = None

        # When
        with pytest.raises(ApiErrors) as error:
            check_has_venue_id(venue_id)

        # Then
        assert error.value.errors['venueId'] == ['Vous devez préciser un identifiant de lieu']

    def test_raises_does_not_raise_exception_when_venue_id(self):
        # Given
        venue_id = 'AE'

        # When
        try:
            check_has_venue_id(venue_id)
        except:
            assert False


class CheckOfferTypeIsValidTest:
    def test_raises_api_error_when_offer_type_is_invalid(self):
        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_type_is_valid('')

        # Then
        assert error.value.errors['type'] == ['Le type de cette offre est inconnu']

    def test_does_not_raise_exception_when_ThingType_is_given(self):
        # When
        try:
            check_offer_type_is_valid(str(ThingType.JEUX_VIDEO))
        except:
            assert False

    def test_does_not_raise_exception_when_EventType_is_given(self):
        # When
        try:
            check_offer_type_is_valid(str(EventType.ACTIVATION))
        except:
            assert False