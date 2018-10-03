import pytest

from utils.test_utils import create_offerer


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
