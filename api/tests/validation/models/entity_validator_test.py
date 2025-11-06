import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.categories import subcategories
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
