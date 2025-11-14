import pcapi.core.offers.factories as offers_factories
from pcapi.core.categories import subcategories
from pcapi.validation.models.entity_validator import validate


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
