import pytest

from models import ApiErrors
from validation.offerers import validate_bank_information


@pytest.mark.standalone
def test_validate_bank_information_does_not_raises_an_error_if_both_iban_and_bic_are_empty():
    # given
    bic = ''
    iban = ''

    # when
    try:
        validate_bank_information(iban, bic)
    except ApiErrors:
        # then
        assert False, 'Empty IBAN and BIC are authorized'


@pytest.mark.standalone
def test_validate_bank_information_does_not_raises_an_error_if_both_iban_and_bic_are_none():
    # given
    bic = None
    iban = None

    # when
    try:
        validate_bank_information(iban, bic)
    except ApiErrors:
        # then
        assert False, 'Empty IBAN and BIC are authorized'


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_both_iban_and_bic_are_invalid():
    # given
    bic = 'dazdazdaz'
    iban = 'zefzezefzeffzef'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert e.value.errors['bic'] == ["Le BIC saisi est invalide"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_iban_is_valid_but_bic_is_not():
    # given
    iban = 'FR7630006000011234567890189'
    bic = 'random bic'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['bic'] == ["Le BIC saisi est invalide"]
    assert 'iban' not in e.value.errors


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_is_valid_but_iban_is_not():
    # given
    iban = 'random iban'
    bic = 'BDFEFR2LCCB'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['iban'] == ["L'IBAN saisi est invalide"]
    assert 'bic' not in e.value.errors


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_8_but_is_unknown():
    # given
    iban = 'FR7630006000011234567890189'
    bic = 'AZRTAZ22'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['bic'] == ["Le BIC saisi est inconnu"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_iban_looks_correct_but_does_not_pass_validation_algorithm():
    # given
    iban = 'FR7630006000011234567890180'
    bic = 'BDFEFR2LCCB'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['iban'] == ["L'IBAN saisi est invalide"]


@pytest.mark.standalone
def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    iban = 'FR7630006000011234567890189'
    bic = 'CITCCWCUDSK'

    # when
    with pytest.raises(ApiErrors) as e:
        validate_bank_information(iban, bic)

    # then
    assert e.value.errors['bic'] == ["Le BIC saisi est inconnu"]
