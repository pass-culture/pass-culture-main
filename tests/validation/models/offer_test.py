from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import ApiErrors
from pcapi.validation.models.offer import validate


def test_should_return_error_message_when_offer_is_digital_and_his_venue_is_not_virtual():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=False)
    thing_offer = create_offer_with_thing_product(venue, is_digital=True)
    api_errors = ApiErrors()

    # When
    api_error = validate(thing_offer, api_errors)

    # Then
    assert api_error.errors["venue"] == [
        'Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"'
    ]


def test_should_return_error_message_when_offer_is_digital_and_its_type_is_offline_only():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True)
    thing_offer = create_offer_with_thing_product(venue, is_digital=True, is_offline_only=True)
    api_errors = ApiErrors()

    # When
    api_error = validate(thing_offer, api_errors)

    # Then
    assert api_error.errors["url"] == ["Une offre de sous-catégorie CARTE_CINE_MULTISEANCES ne peut pas être numérique"]


def test_should_return_error_message_when_offer_is_not_digital_and_his_venue_is_virtual():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True)
    thing_offer = create_offer_with_thing_product(venue, is_digital=False)
    api_errors = ApiErrors()

    # When
    api_error = validate(thing_offer, api_errors)

    # Then
    assert api_error.errors["venue"] == ['Une offre physique ne peut être associée au lieu "Offre numérique"']


def test_should_return_error_messages_when_offer_is_digital_and_offline_and_venue_is_not_virtual():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=False)
    thing_offer = create_offer_with_thing_product(venue, is_digital=True, is_offline_only=True)
    api_errors = ApiErrors()

    # When
    api_error = validate(thing_offer, api_errors)

    # Then
    assert api_error.errors == {
        "url": ["Une offre de sous-catégorie CARTE_CINE_MULTISEANCES ne peut pas être numérique"],
        "venue": ['Une offre numérique doit obligatoirement être associée au lieu "Offre numérique"'],
    }


def test_should_not_return_error_message_when_offer_is_valid():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True)
    thing_offer = create_offer_with_thing_product(venue, is_digital=True)
    api_errors = ApiErrors()

    # When
    api_error = validate(thing_offer, api_errors)

    # Then
    assert api_error.errors == {}
