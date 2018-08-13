import pytest
from sqlalchemy.exc import IntegrityError

from models.venue import TooManyVirtualVenuesException
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_have_address_and_isVirtual(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', is_virtual=True)
    venue.address = '1 test address'

    # When
    with pytest.raises(IntegrityError) as ie:
        venue.save()


@clean_database
@pytest.mark.standalone
def test_offerer_not_isVirtual_cannot_have_null_address(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None, postal_code=None,
                         city=None, departement_code=None, is_virtual=False)

    # When
    with pytest.raises(IntegrityError) as ie:
        venue.save()


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_create_a_second_virtual_venue(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None, postal_code=None,
                         city=None, departement_code=None, is_virtual=True)
    venue.save()

    new_venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None,
                             postal_code=None, city=None, departement_code=None, is_virtual=True)

    # When
    with pytest.raises(TooManyVirtualVenuesException):
        new_venue.save()


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_update_a_second_venue_to_be_virtual(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, address=None, postal_code=None, city=None, departement_code=None, is_virtual=True)
    venue.save()

    new_venue = create_venue(offerer, is_virtual=False)
    new_venue.save()

    # When
    new_venue.isVirtual = True
    new_venue.postalCode = None
    new_venue.address = None
    new_venue.city = None
    new_venue.departementCode = None

    # Then
    with pytest.raises(TooManyVirtualVenuesException):
        new_venue.save()
