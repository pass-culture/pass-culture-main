import pcapi.core.offers.factories as offers_factories
from pcapi.validation.models.generic import validate_generic


def test_should_return_error_when_information_is_mandatory():
    offer = offers_factories.OfferFactory.build(name=None)
    api_error = validate_generic(offer)
    assert api_error.errors == {"name": ["Cette information est obligatoire"]}


def test_should_return_error_when_information_requires_a_string_type():
    offer = offers_factories.OfferFactory.build(name=1234)
    api_error = validate_generic(offer)
    assert api_error.errors == {"name": ["doit être une chaîne de caractères"]}


def test_should_return_error_when_information_requires_an_integer_type():
    offer = offers_factories.OfferFactory.build(durationMinutes="not a number")
    api_error = validate_generic(offer)
    assert api_error.errors == {"durationMinutes": ["doit être un entier"]}


def test_should_return_error_when_information_exceeds_column_size():
    offer = offers_factories.OfferFactory.build(name=141 * "a")
    api_error = validate_generic(offer)
    assert api_error.errors == {"name": ["Vous devez saisir moins de 140 caractères"]}
