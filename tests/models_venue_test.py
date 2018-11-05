import pytest

from models import ApiErrors, PcObject
from models.venue import TooManyVirtualVenuesException
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, create_thing_offer, create_event_offer


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
    offerer = create_offerer('132547698', '1 rue Test', 'Test city', '93000', 'Test offerer')
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
    offerer = create_offerer('132547698', '1 rue Test', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer, address=None, postal_code=None, city=None, departement_code=None, is_virtual=True,
                         siret=None)
    PcObject.check_and_save(venue)

    new_venue = create_venue(offerer, is_virtual=False, siret='13254769898765')
    PcObject.check_and_save(new_venue)

    # When
    new_venue.isVirtual = True
    new_venue.postalCode = None
    new_venue.address = None
    new_venue.city = None
    new_venue.departementCode = None

    # Then
    with pytest.raises(TooManyVirtualVenuesException):
        PcObject.check_and_save(new_venue)


@clean_database
@pytest.mark.standalone
def test_venue_raises_exeption_when_is_virtual_and_has_siret(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, is_virtual=True, siret='12345678912345')

    # when
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


@clean_database
@pytest.mark.standalone
def test_venue_raises_exeption_when_no_siret_and_no_comment(app):
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, siret=None, comment=None)

    # when
    with pytest.raises(ApiErrors):
        PcObject.check_and_save(venue)


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
def test_venue_errors_does_not_raises_an_error_if_both_iban_and_bic_are_empty():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='', iban='')

    # when
    errors = venue.errors()

    # then
    assert not errors.errors


@pytest.mark.standalone
def test_venue_errors_does_not_raises_an_error_if_both_iban_and_bic_are_none():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic=None, iban=None)

    # when
    errors = venue.errors()

    # then
    assert not errors.errors


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_both_iban_and_bic_are_invalid():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='dazdazdaz', iban='zefzezefzeffzef')
    # when
    errors = venue.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert errors.errors['bic'] == ["Le BIC saisi est invalide"]


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_iban_is_valid_but_bic_is_not():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='random bic', iban='FR7630006000011234567890189')
    # when
    errors = venue.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC saisi est invalide"]
    assert 'iban' not in errors.errors


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_bic_is_valid_but_iban_is_not():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='BDFEFR2LCCB', iban='random iban')
    # when
    errors = venue.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert 'bic' not in errors.errors


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_bic_has_correct_length_of_8_but_is_unknown():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='AZRTAZ22', iban='FR7630006000011234567890189')

    # when
    errors = venue.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC saisi est inconnu"]


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_iban_looks_correct_but_does_not_pass_validation_algorithm():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='BDFEFR2LCCB', iban='FR7630006000011234567890180')

    # when
    errors = venue.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='CITCCWCUDSK', iban='FR7630006000011234567890189')

    # when
    errors = venue.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC saisi est inconnu"]


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic=None, iban='FR7630006000011234567890189')

    # when
    errors = venue.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC es manquant"]


@pytest.mark.standalone
def test_venue_errors_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer()
    venue = create_venue(offerer, bic='BDFEFR2LCCB', iban=None)

    # when
    errors = venue.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN es manquant"]
