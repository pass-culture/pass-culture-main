import pcapi.core.finance.factories as finance_factories
from pcapi.validation.models import entity_validator


def test_offerer_errors_raises_an_error_if_both_iban_and_bic_are_empty():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic="", iban="")

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ['L’IBAN renseigné ("") est invalide']
    assert errors.errors["bic"] == ['Le BIC renseigné ("") est invalide']


def test_offerer_errors_raises_an_error_if_both_iban_and_bic_are_none():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic=None, iban=None)

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ["Cette information est obligatoire"]
    assert errors.errors["bic"] == ["Cette information est obligatoire"]


def test_validate_bank_information_raises_an_error_if_both_iban_and_bic_are_invalid():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic="fake_bic", iban="fake_iban")

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ['L’IBAN renseigné ("fake_iban") est invalide']
    assert errors.errors["bic"] == ['Le BIC renseigné ("fake_bic") est invalide']


def test_validate_bank_information_raises_an_error_if_iban_is_valid_but_bic_is_not():
    # given
    bank_information = finance_factories.BankInformationFactory.build(
        bic="fake_bic", iban="FR7630006000011234567890189"
    )

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["bic"] == ['Le BIC renseigné ("fake_bic") est invalide']
    assert "iban" not in errors.errors


def test_validate_bank_information_raises_an_error_if_bic_is_valid_but_iban_is_not():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic="BDFEFR2LCCB", iban="fake_iban")

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ['L’IBAN renseigné ("fake_iban") est invalide']
    assert "bic" not in errors.errors


def test_validate_bank_information_raises_an_error_if_iban_looks_correct_but_does_not_pass_validation_algorithm():
    # given
    bank_information = finance_factories.BankInformationFactory.build(
        bic="BDFEFR2LCCB", iban="FR7630006000011234567890180"
    )

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ['L’IBAN renseigné ("FR7630006000011234567890180") est invalide']


def test_validate_bank_information_raises_an_error_if_bic_has_correct_length_of_11_but_is_unknown():
    # given
    bank_information = finance_factories.BankInformationFactory.build(
        bic="fake_bic", iban="FR7630006000011234567890189"
    )

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["bic"] == ['Le BIC renseigné ("fake_bic") est invalide']


def test_validate_bank_information_raises_an_error_if_bic_is_missing():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic=None, iban="FR7630006000011234567890189")

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["bic"] == ["Cette information est obligatoire"]


def test_validate_bank_information_raises_an_error_if_iban_is_missing():
    # given
    bank_information = finance_factories.BankInformationFactory.build(bic="BDFEFR2LCCB", iban=None)

    # when
    errors = entity_validator.validate(bank_information)

    # then
    assert errors.errors["iban"] == ["Cette information est obligatoire"]
