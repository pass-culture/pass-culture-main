import pytest

from pcapi.core.categories import subcategories
from pcapi.models import ApiErrors
from pcapi.models import EventType
from pcapi.models import ThingType
from pcapi.validation.routes.offers import check_offer_isbn_is_valid
from pcapi.validation.routes.offers import check_offer_name_length_is_valid
from pcapi.validation.routes.offers import check_offer_subcategory_is_valid
from pcapi.validation.routes.offers import check_offer_type_is_valid


class CheckOfferTypeIsValidTest:
    def test_raises_api_error_when_offer_type_is_invalid(self):
        # When
        with pytest.raises(ApiErrors) as error:
            check_offer_type_is_valid("")

        # Then
        assert error.value.errors["type"] == ["Le type de cette offre est inconnu"]

    def test_does_not_raise_exception_when_ThingType_is_given(self):
        check_offer_type_is_valid(str(ThingType.JEUX_VIDEO))

    def test_does_not_raise_exception_when_EventType_is_given(self):
        check_offer_type_is_valid(str(EventType.CINEMA))


class CheckOfferSubcategoryIsValidTest:
    def test_valid_subcategory(self):
        check_offer_subcategory_is_valid(subcategories.LIVRE_PAPIER.id)

    def test_raises_api_error_when_offer_subcategory_is_invalid(self):
        with pytest.raises(ApiErrors) as error:
            check_offer_subcategory_is_valid("TOTO")

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]

    def test_raises_api_error_when_offer_subcategory_is_not_selectable(self):
        with pytest.raises(ApiErrors) as error:
            check_offer_subcategory_is_valid("ACTIVATION_EVENT")

        assert error.value.errors["subcategory"] == [
            "Une offre ne peut être créée ou éditée en utilisant cette sous-catégorie"
        ]


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


class CheckOfferIsbnIsValidTest:
    def test_raises_api_error_when_offer_isbn_is_too_long(self):
        isbn_too_long = "123456789123456789"

        with pytest.raises(ApiErrors) as error:
            check_offer_isbn_is_valid(isbn_too_long)

        assert error.value.errors["isbn"] == ["Format d’ISBN incorrect. Exemple de format correct : 9782020427852"]

    def test_raises_api_error_when_offer_isbn_is_too_short(self):
        isbn_too_short = "123"

        with pytest.raises(ApiErrors) as error:
            check_offer_isbn_is_valid(isbn_too_short)

        assert error.value.errors["isbn"] == ["Format d’ISBN incorrect. Exemple de format correct : 9782020427852"]

    def test_raises_api_error_when_offer_isbn_is_with_alphabets(self):
        isbn_with_alphabets = "12ab45cd67ef8"

        with pytest.raises(ApiErrors) as error:
            check_offer_isbn_is_valid(isbn_with_alphabets)

        assert error.value.errors["isbn"] == ["Format d’ISBN incorrect. Exemple de format correct : 9782020427852"]

    def test_raises_api_with_valid_isbn(self):
        valid_isbn = "9782221247884"

        check_offer_isbn_is_valid(valid_isbn)
