from unittest.mock import patch

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
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

    @pytest.mark.usefixtures("db_session")
    def test_missing_offerer_siren(self):
        venue = offerers_factories.VenueFactory(
            managingOfferer__siren=None,
            siret="12345678901234",
        )
        api_errors = validate(venue)
        assert api_errors.errors == {
            "siren": ["Ce lieu ne peut enregistrer de SIRET car la structure associée n’a pas de SIREN renseigné"]
        }


class BankInformationValidationTest:
    def test_invalid_iban_and_bic(self):
        bank_information = finance_factories.BankInformationFactory.build(bic="1234", iban="1234")
        api_errors = validate(bank_information)
        assert api_errors.errors == {
            "bic": ['Le BIC renseigné ("1234") est invalide'],
            "iban": ['L’IBAN renseigné ("1234") est invalide'],
        }

    def test_valid_iban_and_bic(self):
        bank_information = finance_factories.BankInformationFactory.build(
            bic="AGFBFRCC",
            iban="FR7014508000301971798194B82",
        )
        api_errors = validate(bank_information)
        assert not api_errors.errors

    def test_non_empty_iban_and_bic_with_draft_status(self):
        bank_information = finance_factories.BankInformationFactory.build(
            bic="AGFBFRCC",
            iban="FR7014508000301971798194B82",
            status=BankInformationStatus.DRAFT,
        )
        api_errors = validate(bank_information)
        assert api_errors.errors == {
            "bic": ["Le BIC doit être vide pour le statut DRAFT"],
            "iban": ["L’IBAN doit être vide pour le statut DRAFT"],
        }


class OfferValidationTest:
    def test_digital_offer_with_non_virtual_venue(self):
        venue = offerers_factories.VenueFactory.build()
        offer = offers_factories.DigitalOfferFactory.build(venue=venue)
        api_errors = validate(offer)
        assert api_errors.errors == {
            "venue": ['Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"']
        }

    def test_digital_offer_with_virtual_venue(self):
        offer = offers_factories.DigitalOfferFactory.build()
        api_errors = validate(offer)
        assert not api_errors.errors

    def test_physical_offer_with_virtual_venue(self):
        venue = offerers_factories.VirtualVenueFactory.build()
        offer = offers_factories.OfferFactory.build(venue=venue)
        api_errors = validate(offer)
        assert api_errors.errors == {"venue": ['Une offre physique ne peut être associée au lieu "Offre numérique"']}

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


class ProductValidationTest:
    def test_digital_with_incompatible_subcategory(self):
        product = offers_factories.DigitalProductFactory.build(
            subcategoryId=subcategories.CARTE_CINE_MULTISEANCES.id,
        )
        api_errors = validate(product)
        assert api_errors.errors == {
            "url": ["Un produit de sous-catégorie CARTE_CINE_MULTISEANCES ne peut pas être numérique"]
        }

    def test_digital_with_compatible_subcategory(self):
        product = offers_factories.DigitalProductFactory.build()
        api_errors = validate(product)
        assert not api_errors.errors


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


class UserValidationTest:
    @patch("pcapi.validation.models.user.user_queries.count_users_by_email", lambda email: 0)
    def test_public_name_too_short(self):
        user = users_factories.UserFactory.build(publicName="")
        api_errors = validate(user)
        assert api_errors.errors == {"publicName": ["Tu dois saisir au moins 1 caractères."]}

    @patch("pcapi.validation.models.user.user_queries.count_users_by_email", lambda email: 0)
    def test_valid_public_name(self):
        user = users_factories.UserFactory.build(publicName="Joe la bricole")
        api_errors = validate(user)
        assert not api_errors.errors
