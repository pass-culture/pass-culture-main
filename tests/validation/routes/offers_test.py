import pytest

from pcapi.models import ApiErrors
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.validation.routes.offers import check_edition_for_allocine_offer_is_valid
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_offer_type_is_valid


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


class CheckOfferNameIsValidTest:
    def test_raises_api_error_when_offer_name_is_too_long(self):
        # Given
        offer_title_too_long = 'Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)'

        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_name_length_is_valid(offer_title_too_long)

        # Then
        assert error.value.errors['name'] == ['Le titre de l’offre doit faire au maximum 90 caractères.']

    def test_does_not_raise_exception_when_offer_name_length_is_valid(self):
        # Given
        offer_title_less_than_90_characters = 'Nom de moins de quatre-vingt-dix caractères'

        # When
        try:
            check_offer_name_length_is_valid(offer_title_less_than_90_characters)
        except:
            assert False


class CheckEditionForAllocineOfferIsValidTest:
    def test_pass_when_fields_edited(self):
        # Given
        payload = {}

        # Then
        try:
            check_edition_for_allocine_offer_is_valid(payload)
        except:
            assert False

    def test_raises_exception_when_fields_are_not_editable(self):
        # Given
        payload = {
            'bookingEmail': 'offer@example.com',
            'isNational': True,
            'name': 'Nouvelle offre'
        }

        # When
        with pytest.raises(ApiErrors) as error:
            check_edition_for_allocine_offer_is_valid(payload)

        # Then
        assert error.value.errors['bookingEmail'] == ['Vous ne pouvez pas modifier ce champ']
        assert error.value.errors['isNational'] == ['Vous ne pouvez pas modifier ce champ']
        assert error.value.errors['name'] == ['Vous ne pouvez pas modifier ce champ']
