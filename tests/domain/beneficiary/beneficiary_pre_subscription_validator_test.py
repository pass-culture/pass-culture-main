from datetime import datetime

import pytest

from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsADuplicate
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsNotEligible
from pcapi.domain.beneficiary_pre_subscription.exceptions import CantRegisterBeneficiary
from pcapi.domain.beneficiary_pre_subscription.validator import validate

from tests.domain_creators.generic_creators import create_domain_beneficiary_pre_subcription


@pytest.mark.usefixtures("db_session")
def test_should_not_raise_exception_for_valid_beneficiary(app):
    # Given
    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription()

    try:
        # When
        validate(beneficiary_pre_subcription)
    except CantRegisterBeneficiary:
        # Then
        assert pytest.fail("Should not raise an exception when email not given")


@pytest.mark.usefixtures("db_session")
def test_raises_if_email_already_taken_by_beneficiary(app):
    # Given
    email = "email@example.org"
    existing_user = users_factories.BeneficiaryGrant18Factory(email=email)

    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(email=email)

    # When
    with pytest.raises(BeneficiaryIsADuplicate) as error:
        validate(beneficiary_pre_subcription, preexisting_account=existing_user)

    # Then
    assert str(error.value) == f"Email {email} is already taken."


@pytest.mark.usefixtures("db_session")
def test_validates_for_non_beneficiary_with_same_mail(app):
    email = "email@example.org"
    existing_user = users_factories.UserFactory(email=email, isBeneficiary=False, isEmailValidated=True)

    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(email=email)

    # Should not raise an exception
    validate(beneficiary_pre_subcription, preexisting_account=existing_user)


@pytest.mark.usefixtures("db_session")
def test_doesnt_raise_if_email_not_taken(app):
    # Given
    users_factories.UserFactory(email="email@example.org")

    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(email="different.email@example.org")

    try:
        # When
        validate(beneficiary_pre_subcription)
    except CantRegisterBeneficiary:
        # Then
        assert pytest.fail("Should not raise an exception when email not given")


@pytest.mark.usefixtures("db_session")
def test_raises_if_duplicate(app):
    # Given
    first_name = "John"
    last_name = "Doe"
    date_of_birth = datetime(1993, 2, 2)
    existing_user = users_factories.BeneficiaryGrant18Factory(
        firstName=first_name, lastName=last_name, dateOfBirth=date_of_birth
    )

    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(
        first_name=first_name, last_name=last_name, date_of_birth=date_of_birth
    )

    # When
    with pytest.raises(BeneficiaryIsADuplicate) as error:
        validate(beneficiary_pre_subcription)

    # Then
    assert str(error.value) == f"User with id {existing_user.id} is a duplicate."


@pytest.mark.usefixtures("db_session")
def test_doesnt_raise_if_no_exact_duplicate(app):
    # Given
    first_name = "John"
    last_name = "Doe"
    date_of_birth = datetime(1993, 2, 2)
    users_factories.UserFactory(firstName="Joe", lastName=last_name, dateOfBirth=date_of_birth, email="e1@example.com")
    users_factories.UserFactory(
        firstName=first_name, lastName="Dane", dateOfBirth=date_of_birth, email="e2@example.com"
    )
    users_factories.UserFactory(
        firstName=first_name, lastName=last_name, dateOfBirth=datetime(1992, 2, 2), email="e3@example.com"
    )

    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(
        first_name=first_name, last_name=last_name, date_of_birth=date_of_birth
    )

    try:
        # When
        validate(beneficiary_pre_subcription)
    except CantRegisterBeneficiary:
        # Then
        assert pytest.fail("Should not raise an exception when email not given")


@override_features(WHOLE_FRANCE_OPENING=False)
@pytest.mark.parametrize("postal_code", ["36000", "36034", "97400"])
@pytest.mark.usefixtures("db_session")
def test_raises_if_not_eligible_legacy_behaviour(postal_code):
    # Given
    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(postal_code=postal_code)

    # When
    with pytest.raises(BeneficiaryIsNotEligible) as error:
        validate(beneficiary_pre_subcription)

    # Then
    assert str(error.value) == f"Postal code {postal_code} is not eligible."


@override_features(WHOLE_FRANCE_OPENING=False)
@pytest.mark.parametrize("postal_code", ["34000", "34898", "97340"])
@pytest.mark.usefixtures("db_session")
def test_should_not_raise_if_eligible_legacy_behaviour(postal_code):
    # Given
    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(postal_code=postal_code)

    try:
        # When
        validate(beneficiary_pre_subcription)
    except CantRegisterBeneficiary:
        # Then
        assert pytest.fail("Should not raise when postal code is eligible")


@override_features(WHOLE_FRANCE_OPENING=True)
@pytest.mark.parametrize("postal_code", ["98735", "98800", "98800"])
@pytest.mark.usefixtures("db_session")
def test_raises_if_not_eligible(postal_code):
    # Given
    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(postal_code=postal_code)

    # When
    with pytest.raises(BeneficiaryIsNotEligible) as error:
        validate(beneficiary_pre_subcription)

    # Then
    assert str(error.value) == f"Postal code {postal_code} is not eligible."


@override_features(WHOLE_FRANCE_OPENING=True)
@pytest.mark.parametrize("postal_code", ["36000", "36034", "97400"])
@pytest.mark.usefixtures("db_session")
def test_should_not_raise_if_eligible(postal_code):
    # Given
    beneficiary_pre_subcription = create_domain_beneficiary_pre_subcription(postal_code=postal_code)

    try:
        # When
        validate(beneficiary_pre_subcription)
    except CantRegisterBeneficiary:
        # Then
        assert pytest.fail("Should not raise when postal code is eligible")
