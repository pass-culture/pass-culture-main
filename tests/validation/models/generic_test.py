from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.validation.models.generic import validate_generic


def test_should_return_error_when_information_is_mandatory():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue, thing_name=None)

    # When
    api_error = validate_generic(offer)

    # Then
    assert api_error.errors == {"name": ["Cette information est obligatoire"]}


def test_should_return_error_when_information_requires_a_string_type():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(venue, thing_name=1234)

    # When
    api_error = validate_generic(offer)

    # Then
    assert api_error.errors == {"name": ["doit être une chaîne de caractères"]}


def test_should_return_error_when_information_requires_an_integer_type():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_event_product(venue, duration_minutes="1")

    # When
    api_error = validate_generic(offer)

    # Then
    assert api_error.errors == {"durationMinutes": ["doit être un entier"]}


def test_should_return_error_when_information_exceeds_column_size():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_offer_with_thing_product(
        venue,
        thing_name="qBWnUS4JTt5qPNkOv02oaBu3H7GfMY2H9vgocxsYNJrfvHuQaaRJn"
        "2AI9V93Wds1nJS8NqBhJVNYzaNrgS1eldyn4HsIiUU3UqmPwPGHAcQ"
        "e451TBYUO0xYiyQzTMOKxcYMJsd9FBbygb",
    )

    # When
    api_error = validate_generic(offer)

    # Then
    assert api_error.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
