import pytest

from models import PcObject, ApiErrors
from tests.conftest import clean_database
from utils.test_utils import create_offerer, create_venue, create_thing_offer, create_event_offer


@pytest.mark.standalone
def test_offerer_errors_does_not_raises_an_error_if_both_iban_and_bic_are_empty():
    # given
    offerer = create_offerer(bic='', iban='')

    # when
    errors = offerer.errors()

    # then
    assert not errors.errors


@pytest.mark.standalone
def test_offerer_errors_does_not_raises_an_error_if_both_iban_and_bic_are_none():
    # given
    offerer = create_offerer(bic=None, iban=None)

    # when
    errors = offerer.errors()

    # then
    assert not errors.errors


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_both_iban_and_bic_are_invalid():
    # given
    offerer = create_offerer(bic='dazdazdaz', iban='zefzezefzeffzef')
    # when
    errors = offerer.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert errors.errors['bic'] == ["Le BIC saisi est invalide"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_iban_is_valid_but_bic_is_not():
    # given
    offerer = create_offerer(bic='random bic', iban='FR7630006000011234567890189')
    # when
    errors = offerer.errors()


    # then
    assert errors.errors['bic'] == ["Le BIC saisi est invalide"]
    assert 'iban' not in errors.errors


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_is_valid_but_iban_is_not():
    # given
    offerer = create_offerer(bic='BDFEFR2LCCB', iban='random iban')
    # when
    errors = offerer.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert 'bic' not in errors.errors


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_8_but_is_unknown():
    # given
    offerer = create_offerer(bic='AZRTAZ22', iban='FR7630006000011234567890189')

    # when
    errors = offerer.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC saisi est inconnu"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_iban_looks_correct_but_does_not_pass_validation_algorithm():
    # given
    offerer = create_offerer(bic='BDFEFR2LCCB', iban='FR7630006000011234567890180')

    # when
    errors = offerer.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN saisi est invalide"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer(bic='CITCCWCUDSK', iban='FR7630006000011234567890189')

    # when
    errors = offerer.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC saisi est inconnu"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer(bic=None, iban='FR7630006000011234567890189')

    # when
    errors = offerer.errors()

    # then
    assert errors.errors['bic'] == ["Le BIC es manquant"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    offerer = create_offerer(bic='BDFEFR2LCCB', iban=None)

    # when
    errors = offerer.errors()

    # then
    assert errors.errors['iban'] == ["L'IBAN es manquant"]


@pytest.mark.standalone
@clean_database
def test_nOffers(app):
    # given
    offerer = create_offerer()
    venue_1 = create_venue(offerer, siret='12345678912345')
    venue_2 = create_venue(offerer, siret='67891234512345')
    venue_3 = create_venue(offerer, siret='23451234567891')
    offer_v1_1 = create_thing_offer(venue_1)
    offer_v1_2 = create_event_offer(venue_1)
    offer_v2_1 = create_event_offer(venue_2)
    offer_v2_2 = create_event_offer(venue_2)
    offer_v3_1 = create_thing_offer(venue_3)
    PcObject.check_and_save(offer_v1_1, offer_v1_2, offer_v2_1, offer_v2_2, offer_v3_1)

    # when
    n_offers = offerer.nOffers

    # then
    assert n_offers == 5


@pytest.mark.standalone
@clean_database
def test_offerer_can_have_null_address(app):
    # given
    offerer = create_offerer(address=None)

    try:
        # when
        PcObject.check_and_save(offerer)
    except ApiErrors:
        # then
        assert False
