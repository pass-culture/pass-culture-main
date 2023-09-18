import pytest

from pcapi.models.api_errors import ApiErrors
from pcapi.validation.routes.offers import check_offer_name_length_is_valid


class CheckOfferNameIsValidTest:
    def test_raises_api_error_when_offer_name_is_too_long(self):
        # Given
        offer_title_too_long = (
            "Nom vraiment très long excédant la taille maximale (nom de plus de quatre-vingt-dix caractères)"
        )

        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_name_length_is_valid(offer_title_too_long)

        # Then
        assert error.value.errors["name"] == ["Le titre de l’offre doit faire au maximum 90 caractères."]

    def test_does_not_raise_exception_when_offer_name_length_is_valid(self):
        # Given
        offer_title_less_than_90_characters = "Nom de moins de quatre-vingt-dix caractères"

        # The the following should not raise
        check_offer_name_length_is_valid(offer_title_less_than_90_characters)
