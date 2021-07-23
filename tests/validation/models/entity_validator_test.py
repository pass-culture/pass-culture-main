from unittest.mock import patch

from pcapi.core.users import factories as users_factories
from pcapi.model_creators.generic_creators import create_bank_information
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_subcategory
from pcapi.validation.models.entity_validator import validate


def test_should_return_errors_when_invalid_address():
    # Given
    offerer = create_offerer(postal_code="abcde")

    # When
    api_errors = validate(offerer)

    # Then
    assert api_errors.errors == {"postalCode": ["Ce code postal est invalide"]}


def test_should_not_return_errors_when_valid_address():
    # Given
    offerer = create_offerer(postal_code="75000")

    # When
    api_errors = validate(offerer)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_bank_information():
    # Given
    bank_information = create_bank_information(bic="1234", iban="1234")

    # When
    api_errors = validate(bank_information)

    # Then
    assert api_errors.errors == {
        "bic": ['Le BIC renseigné ("1234") est invalide'],
        "iban": ['L’IBAN renseigné ("1234") est invalide'],
    }


def test_should_not_return_errors_when_valid_bank_information():
    # Given
    bank_information = create_bank_information(bic="AGFBFRCC", iban="FR7014508000301971798194B82")

    # When
    api_errors = validate(bank_information)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_offer():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=False)
    offer = create_offer_with_thing_product(venue, is_digital=True)

    # When
    api_errors = validate(offer)

    # Then
    assert api_errors.errors == {
        "venue": ['Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"']
    }


def test_should_not_return_errors_when_valid_offer():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True)
    offer = create_offer_with_thing_product(venue, is_digital=True)

    # When
    api_errors = validate(offer)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_offerer():
    # Given
    offerer = create_offerer(siren="1")

    # When
    api_errors = validate(offerer)

    # Then
    assert api_errors.errors == {"siren": ["Ce code SIREN est invalide"]}


def test_should_not_return_errors_when_valid_offerer():
    # Given
    offerer = create_offerer(siren="123456789")

    # When
    api_errors = validate(offerer)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_product():
    # Given
    product = create_product_with_thing_subcategory(is_offline_only=True, is_digital=True)

    # When
    api_errors = validate(product)

    # Then
    assert api_errors.errors == {"url": ["Une offre de type Cinéma - cartes d'abonnement ne peut pas être numérique"]}


def test_should_return_errors_when_valid_product():
    # Given
    product = create_product_with_thing_subcategory()

    # When
    api_errors = validate(product)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_stock():
    # Given
    stock = create_stock(quantity=-1)

    # When
    api_errors = validate(stock)

    # Then
    assert api_errors.errors == {"quantity": ["La quantité doit être positive."]}


def test_should_not_return_errors_when_valid_stock():
    # Given
    stock = create_stock(quantity=1)

    # When
    api_errors = validate(stock)

    # Then
    assert api_errors.errors == {}


@patch("pcapi.validation.models.user.user_queries.count_users_by_email")
def test_should_return_errors_when_invalid_user(mock_count_users_by_email, app):
    # Given
    user = users_factories.UserFactory.build(publicName="")
    mock_count_users_by_email.return_value = 0

    # When
    api_errors = validate(user)

    # Then
    assert api_errors.errors == {"publicName": ["Tu dois saisir au moins 1 caractères."]}


@patch("pcapi.validation.models.user.user_queries.count_users_by_email")
def test_should_not_return_errors_when_valid_user(mock_count_users_by_email, app):
    # Given
    user = users_factories.UserFactory.build(publicName="Joe la bricole")
    mock_count_users_by_email.return_value = 0

    # When
    api_errors = validate(user)

    # Then
    assert api_errors.errors == {}


def test_should_return_errors_when_invalid_venue():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, siret="123")

    # When
    api_errors = validate(venue)

    # Then
    assert api_errors.errors == {"siret": ["Ce code SIRET est invalide : 123"]}


def test_should_not_return_errors_when_valid_venue():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, siret="44229377500031")

    # When
    api_errors = validate(venue)

    # Then
    assert api_errors.errors == {}


def test_should_return_multiple_errors_when_invalid_offerer_and_address():
    # Given
    offerer = create_offerer(siren="1", postal_code="123")

    # When
    api_errors = validate(offerer)

    # Then
    assert api_errors.errors == {"postalCode": ["Ce code postal est invalide"], "siren": ["Ce code SIREN est invalide"]}
