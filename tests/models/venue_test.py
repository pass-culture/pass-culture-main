import pytest

from models import ApiErrors, PcObject
from models.venue import TooManyVirtualVenuesException
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_venue, create_thing_offer, create_event_offer, \
    create_bank_information


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_have_address_and_isVirtual(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', is_virtual=True, siret=None)
    venue.address = '1 test address'

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_offerer_not_isVirtual_cannot_have_null_address(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None, postal_code=None,
                         city=None, departement_code=None, is_virtual=False)

    # When
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_create_a_second_virtual_venue(app):
    # Given
    offerer = create_offerer('123456789', '1 rue Test', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None, postal_code=None,
                         city=None, departement_code=None, is_virtual=True, siret=None)
    PcObject.check_and_save(venue)

    new_venue = create_venue(offerer, name='Venue_name', booking_email='booking@email.com', address=None,
                             postal_code=None, city=None, departement_code=None, is_virtual=True, siret=None)

    # When
    with pytest.raises(TooManyVirtualVenuesException):
        PcObject.check_and_save(new_venue)


@clean_database
@pytest.mark.standalone
def test_offerer_cannot_update_a_second_venue_to_be_virtual(app):
    # Given
    siren = '132547698'
    offerer = create_offerer(siren, '1 rue Test', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, address=None, postal_code=None, city=None, departement_code=None, is_virtual=True,
                         siret=None)
    PcObject.check_and_save(venue)

    new_venue = create_venue(offerer, is_virtual=False, siret=siren + '98765')
    PcObject.check_and_save(new_venue)

    # When
    new_venue.isVirtual = True
    new_venue.postalCode = None
    new_venue.address = None
    new_venue.city = None
    new_venue.departementCode = None
    new_venue.siret = None

    # Then
    with pytest.raises(TooManyVirtualVenuesException):
        PcObject.check_and_save(new_venue)


@clean_database
@pytest.mark.standalone
def test_venue_raises_exception_when_is_virtual_and_has_siret(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret='12345678912345')

    # when
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_venue_raises_exception_when_no_siret_and_no_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment=None)

    # when
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_venue_raises_exception_when_siret_and_comment_but_virtual(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment="hello I've comment and siret but i'm virtual", is_virtual=True)

    # when
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_venue_can_have_siret_and_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret="02345678912345", comment="hello I have some comment and siret !", is_virtual=False)
    PcObject.check_and_save(venue)

    # when
    siret = venue.siret

    assert siret == "02345678912345"


@clean_database
@pytest.mark.standalone
def test_venue_can_have_no_siret_but_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment="hello I have some comment but no siret :(", is_virtual=False)
    PcObject.check_and_save(venue)

    # when
    comment = venue.comment

    assert comment == "hello I have some comment but no siret :("


@pytest.mark.standalone
@clean_database
def test_nOffers(app):
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer_1 = create_thing_offer(venue)
    offer_2 = create_event_offer(venue)
    offer_4 = create_event_offer(venue)
    offer_5 = create_thing_offer(venue)
    PcObject.check_and_save(offer_1, offer_2, offer_4, offer_5)

    # when
    n_offers = venue.nOffers

    # then
    assert n_offers == 4


@pytest.mark.standalone
class VenueBankInformationTest:
    @clean_database
    def test_bic_property_returns_bank_information_bic_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')
        bank_information = create_bank_information(bic='BDFEFR2LCCB', id_at_providers='12345678912345', venue=venue)
        PcObject.check_and_save(bank_information)

        # When
        bic = venue.bic

        # Then
        assert bic == 'BDFEFR2LCCB'

    @clean_database
    def test_bic_property_returns_none_when_does_not_have_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')
        PcObject.check_and_save(venue)

        # When
        bic = venue.bic

        # Then
        assert bic is None

    @clean_database
    def test_iban_property_returns_bank_information_iban_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')
        bank_information = create_bank_information(iban='FR7630007000111234567890144', id_at_providers='12345678912345',
                                                   venue=venue)
        PcObject.check_and_save(bank_information)

        # When
        iban = venue.iban

        # Then
        assert iban == 'FR7630007000111234567890144'

    @clean_database
    def test_iban_property_returns_none_when_venue_has_bank_information(self, app):
        # Given
        offerer = create_offerer(siren='123456789')
        venue = create_venue(offerer, siret='12345678912345')
        PcObject.check_and_save(venue)

        # When
        iban = venue.iban

        # Then
        assert iban is None
