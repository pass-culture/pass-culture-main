from repository import repository
from tests.model_creators.generic_creators import create_bank_information


def test_offerer_errors_raises_an_error_if_both_iban_and_bic_are_empty(app):
    # given
    bank_information = create_bank_information(bic='', iban='')

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["L'IBAN renseigné (\"\") est invalide"]
    assert errors.errors['bic'] == ["Le BIC renseigné (\"\") est invalide"]


def test_offerer_errors_raises_an_error_if_both_iban_and_bic_are_none(app):
    # given
    bank_information = create_bank_information(bic=None, iban=None)

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["Cette information est obligatoire"]
    assert errors.errors['bic'] == ["Cette information est obligatoire"]


def test_validate_bank_information_raises_an_error_if_both_iban_and_bic_are_invalid(app):
    # given
    bank_information = create_bank_information(bic='dazdazdaz', iban='zefzezefzeffzef')
    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["L'IBAN renseigné (\"zefzezefzeffzef\") est invalide"]
    assert errors.errors['bic'] == ["Le BIC renseigné (\"dazdazdaz\") est invalide"]


def test_validate_bank_information_raises_an_error_if_iban_is_valid_but_bic_is_not(app):
    # given
    bank_information = create_bank_information(bic='random bic', iban='FR7630006000011234567890189')
    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['bic'] == ["Le BIC renseigné (\"random bic\") est invalide"]
    assert 'iban' not in errors.errors


def test_validate_bank_information_raises_an_error_if_bic_is_valid_but_iban_is_not(app):
    # given
    bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='random iban')
    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["L'IBAN renseigné (\"random iban\") est invalide"]
    assert 'bic' not in errors.errors


def test_validate_bank_information_raises_an_error_if_iban_looks_correct_but_does_not_pass_validation_algorithm(app):
    # given
    bank_information = create_bank_information(bic='BDFEFR2LCCB', iban='FR7630006000011234567890180')

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["L'IBAN renseigné (\"FR7630006000011234567890180\") est invalide"]


def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown(app):
    # given
    bank_information = create_bank_information(bic='ABCDEFGHIKL', iban='FR7630006000011234567890189')

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['bic'] == ["Le BIC renseigné (\"ABCDEFGHIKL\") est invalide"]


def test_validate_bank_information_raises_an_error_if_bic_is_missing(app):
    # given
    bank_information = create_bank_information(bic=None, iban='FR7630006000011234567890189')

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['bic'] == ["Cette information est obligatoire"]


def test_validate_bank_information_raises_an_error_if_iban_is_missing(app):
    # given
    bank_information = create_bank_information(bic='BDFEFR2LCCB', iban=None)

    # when
    errors = repository.errors(bank_information)

    # then
    assert errors.errors['iban'] == ["Cette information est obligatoire"]
