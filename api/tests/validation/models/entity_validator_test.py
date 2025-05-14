import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.validation.models.entity_validator import validate


class OffererValidationTest:
    def test_invalid_postal_code(self):
        offerer = offerers_factories.OffererFactory.build(postalCode="abcde")
        api_errors = validate(offerer)
        assert api_errors.errors == {"postalCode": ["Ce code postal est invalide"]}

    def test_valid_postal_code(self):
        offerer = offerers_factories.OffererFactory.build(postalCode="12345")
        api_errors = validate(offerer)
        assert not api_errors.errors

    def test_invalid_siren_with_incorrect_with_length(self):
        offerer = offerers_factories.OffererFactory.build(siren="1")
        api_errors = validate(offerer)
        assert api_errors.errors == {"siren": ["Ce code SIREN est invalide"]}

    def test_invalid_empty_siren(self):
        offerer = offerers_factories.OffererFactory.build(siren="")
        api_errors = validate(offerer)
        assert api_errors.errors == {"siren": ["Ce code SIREN est invalide"]}

    def test_valid_siren(self):
        offerer = offerers_factories.OffererFactory.build(siren="123456789")
        api_errors = validate(offerer)
        assert not api_errors.errors


class VenueValidationTest:
    def test_invalid_siret(self):
        venue = offerers_factories.VenueFactory.build(siret="123")
        api_errors = validate(venue)
        assert api_errors.errors == {"siret": ["Ce code SIRET est invalide : 123"]}

    def test_valid_siret(self):
        venue = offerers_factories.VenueFactory.build(siret="12345678901234")
        api_errors = validate(venue)
        assert api_errors.errors == {}

    @pytest.mark.usefixtures("db_session")
    def test_siren_and_siret_mismatch(self):
        venue = offerers_factories.VenueFactory(
            managingOfferer__siren="987654321",
            siret="12345678901234",
        )
        api_errors = validate(venue)
        assert api_errors.errors == {"siret": ["Le code SIRET doit correspondre à un établissement de votre structure"]}


class OfferValidationTest:
    def test_digital_offer_with_virtual_venue(self):
        offer = offers_factories.DigitalOfferFactory.build()
        api_errors = validate(offer)
        assert not api_errors.errors

    def test_physical_offer_with_non_virtual_venue(self):
        offer = offers_factories.OfferFactory.build()
        api_errors = validate(offer)
        assert not api_errors.errors

    def test_digital_offer_with_incompatible_subcategory(self):
        offer = offers_factories.DigitalOfferFactory.build(
            subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
        )
        api_errors = validate(offer)
        assert api_errors.errors == {
            "url": ["Une offre de sous-catégorie Carte cinéma multi-séances ne peut pas être numérique"]
        }


class StockValidationTest:
    def test_invalid_quantity(self):
        stock = offers_factories.StockFactory.build(quantity=-1)
        api_errors = validate(stock)
        assert api_errors.errors == {"quantity": ["La quantité doit être positive."]}

    def test_valid_finite_quantity(self):
        stock = offers_factories.StockFactory.build(quantity=1)
        api_errors = validate(stock)
        assert not api_errors.errors

    def test_valid_infinite_quantity(self):
        stock = offers_factories.StockFactory.build(quantity=None)
        api_errors = validate(stock)
        assert not api_errors.errors
