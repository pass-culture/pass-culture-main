from models import ApiErrors
from repository import repository
import pytest
from model_creators.generic_creators import create_offerer, create_venue
from validation.models.venue import validate


def test_should_return_error_when_siret_is_invalid():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, siret="123")
    api_errors = ApiErrors()

    # When
    validate(venue=venue, api_errors=api_errors)

    # Then
    assert api_errors.errors == {'siret': ['Ce code SIRET est invalide : 123']}


def test_should_return_error_when_address_is_invalid():
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer, postal_code="123")
    api_errors = ApiErrors()

    # When
    validate(venue=venue, api_errors=api_errors)

    # Then
    assert api_errors.errors == {'postalCode': ['Ce code postal est invalide']}


@pytest.mark.usefixtures("db_session")
def test_should_return_error_when_offerer_has_no_siren(app):
    # Given
    offerer = create_offerer(siren=None)
    venue = create_venue(offerer)
    repository.save(venue)
    api_errors = ApiErrors()

    # When
    validate(venue=venue, api_errors=api_errors)

    # Then
    assert api_errors.errors == {
        'siren': ['Ce lieu ne peut enregistrer de SIRET car la structure associée n’a pas de SIREN renseigné'],
    }


@pytest.mark.usefixtures("db_session")
def test_should_return_error_when_venue_does_not_belong_to_offerer(app):
    # Given
    offerer = create_offerer(siren="1")
    venue = create_venue(offerer, siret="41816609600069")
    repository.save(venue)
    api_errors = ApiErrors()

    # When
    validate(venue=venue, api_errors=api_errors)

    # Then
    assert api_errors.errors == {
        'siret': ['Le code SIRET doit correspondre à un établissement de votre structure']
    }
