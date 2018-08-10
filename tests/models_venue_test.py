import pytest
from sqlalchemy.exc import IntegrityError

from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_have_address_and_isVirtual(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, 'booking@email.com', address='1 test address', postalCode='93000', city='test city', name='Venue_name',
                         departementCode='93', isVirtual=True)

    # When
    with pytest.raises(IntegrityError) as ie:
        venue.save()


@clean_database
@pytest.mark.standalone
def test_offerer_not_isVirtual_cannot_have_null_address(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    offerer.save()

    venue = create_venue(offerer, 'booking@email.com', address=None, postalCode=None, city=None, name='Venue_name',
                         departementCode=None, isVirtual=False)

    # When
    with pytest.raises(IntegrityError) as ie:
        venue.save()
        # Then

# @pytest.mark.standalone
# def test_offerer_cannot_have_two_virtual_venues(app):
#     # Given
#     offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
#     offerer.save()
#
#     venue = create_venue(offerer, 'booking@email.com', address=None, postalCode=None, city=None, name='Venue_name',
#                          departementCode=None, isVirtual=True)
#     venue.save()
#
#     new_venue = create_venue(offerer, 'booking@email.com', address=None, postalCode=None, city=None, name='Venue_name',
#                              departementCode=None, isVirtual=True)
#
#     # When
#     with pytest.raises(IntegrityError) as ie:
#         new_venue.save()
#         # Then
#         print(ie)
#         assert 'isVirtual' in str(ie.orig)