from datetime import datetime
from typing import Optional

from pcapi.core.fraud import api as fraud_api
from pcapi.core.subscription.models import BeneficiaryPreSubscription
from pcapi.core.users.models import User
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsADuplicate
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsNotEligible
from pcapi.domain.beneficiary_pre_subscription.exceptions import IdPieceNumberDuplicate
from pcapi.domain.beneficiary_pre_subscription.exceptions import SuspiciousFraudDetected
from pcapi.models.feature import FeatureToggle
from pcapi.repository.user_queries import find_beneficiary_by_civility
from pcapi.repository.user_queries import find_user_by_email


ELIGIBLE_DEPARTMENTS = {
    "08",
    "22",
    "25",
    "29",
    "34",
    "35",
    "56",
    "58",
    "67",
    "71",
    "84",
    "93",
    "94",
    "973",
}

EXCLUDED_DEPARTMENTS = {
    "984",  # Terres australes et antarctiques françaises
    "987",  # Polynésie Française
    "988",  # Nouvelle-Calédonie
}


def _is_postal_code_eligible(code: Optional[str]) -> bool:
    # departmentCode can now be null
    if not code:
        return True

    # FIXME (dbaty, 2020-01-14): remove this block once we have opened
    # to (almost) all departments.
    # Legacy behaviour: only a few departments are eligible.
    if not FeatureToggle.WHOLE_FRANCE_OPENING.is_active():
        for department in ELIGIBLE_DEPARTMENTS:
            if code.startswith(department):
                return True
        return False

    # New behaviour: all departments are eligible, except a few.
    for department in EXCLUDED_DEPARTMENTS:
        if code.startswith(department):
            return False
    return True


def get_beneficiary_duplicates(first_name: str, last_name: str, date_of_birth: datetime) -> list[User]:
    return find_beneficiary_by_civility(first_name=first_name, last_name=last_name, date_of_birth=date_of_birth)


def _check_email_is_not_taken(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    email = beneficiary_pre_subscription.email

    if find_user_by_email(email):
        raise BeneficiaryIsADuplicate(f"Email {email} is already taken.")


def _check_department_is_eligible(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    postal_code = beneficiary_pre_subscription.postal_code

    if not _is_postal_code_eligible(postal_code):
        raise BeneficiaryIsNotEligible(f"Postal code {postal_code} is not eligible.")


def _check_not_a_duplicate(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    duplicates = get_beneficiary_duplicates(
        first_name=beneficiary_pre_subscription.first_name,
        last_name=beneficiary_pre_subscription.last_name,
        date_of_birth=beneficiary_pre_subscription.date_of_birth,
    )

    if duplicates:
        raise BeneficiaryIsADuplicate(f"User with id {duplicates[0].id} is a duplicate.")


def _check_id_piece_number_format(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    if not fraud_api.validate_id_piece_number_format_fraud_item(beneficiary_pre_subscription.id_piece_number):
        raise SuspiciousFraudDetected(f"id piece number n°{beneficiary_pre_subscription.id_piece_number} is invalid")


def _check_id_piece_number_is_unique(beneficiary_pre_subscription: BeneficiaryPreSubscription) -> None:
    if not FeatureToggle.ENABLE_IDCHECK_FRAUD_CONTROLS.is_active():
        return

    # avoid checks on duplicate id piece number if Jouve's result on the id piece number are already done
    if beneficiary_pre_subscription.fraud_fields:
        fraud_controls = {x.key: x for x in beneficiary_pre_subscription.fraud_fields["non_blocking_controls"]}
        id_fraud_control = fraud_controls.get("bodyPieceNumberCtrl")
        if id_fraud_control and not id_fraud_control.valid:
            return
    if User.query.filter(User.idPieceNumber == beneficiary_pre_subscription.id_piece_number).count() > 0:
        raise IdPieceNumberDuplicate(f"id piece number n°{beneficiary_pre_subscription.id_piece_number} already taken")


def validate(
    beneficiary_pre_subscription: BeneficiaryPreSubscription,
    preexisting_account: User = None,
    ignore_id_piece_number_field: bool = False,
) -> None:
    _check_department_is_eligible(beneficiary_pre_subscription)
    if not preexisting_account:
        _check_email_is_not_taken(beneficiary_pre_subscription)
    else:
        if preexisting_account.isBeneficiary or not preexisting_account.isEmailValidated:
            raise BeneficiaryIsADuplicate(f"Email {beneficiary_pre_subscription.email} is already taken.")
    _check_not_a_duplicate(beneficiary_pre_subscription)
    if not ignore_id_piece_number_field:
        _check_id_piece_number_format(beneficiary_pre_subscription)
        _check_id_piece_number_is_unique(beneficiary_pre_subscription)
