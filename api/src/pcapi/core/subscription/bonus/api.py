import dataclasses
import datetime
import logging
import typing

from dateutil.relativedelta import relativedelta

from pcapi import settings
from pcapi.connectors import api_particulier
from pcapi.core.external.attributes import api as external_attributes_api
from pcapi.core.external.batch import trigger_events
from pcapi.core.finance import deposit_api
from pcapi.core.finance import models as finance_models
from pcapi.core.mails import transactional as transactional_mails
from pcapi.core.subscription import models as subscription_models
from pcapi.core.subscription.bonus import constants as bonus_constants
from pcapi.core.subscription.bonus import schemas as bonus_schemas
from pcapi.core.subscription.bonus import staging_api
from pcapi.core.users import models as users_models
from pcapi.models import db
from pcapi.utils.clean_accents import clean_accents
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class _ApiParticulierResult[
    ResponseT: (
        api_particulier.QuotientFamilialResponse,
        api_particulier.DisabledAdultAllowanceResponse,
        api_particulier.DisabledChildEducationAllowanceResponse,
    )
]:
    response: ResponseT | None
    status: subscription_models.FraudCheckStatus
    reason_codes: list[subscription_models.FraudReasonCode]
    http_status_code: int
    error_code: str | None = None


def apply_for_quotient_familial_bonus(quotient_familial_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    """
    Gets the lowest Quotient Familial from the fraud check custodian, over the fraud check beneficiary seventeenth year,
    and updates the fraud check. Then gives the bonus recredit to the beneficiary if eligible.
    """
    user = quotient_familial_fraud_check.user
    if not deposit_api.can_receive_bonus_credit(user):
        logger.error("trying to apply for bonus when not able to receive said bonus")
        return

    source_data = quotient_familial_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.QuotientFamilialBonusCreditContent):
        raise ValueError(f"QuotientFamilialBonusCreditContent was expected while {type(source_data)} was given")

    qf_result = _call_api_particulier(
        quotient_familial_fraud_check,
        lambda: _get_user_quotient_familial_response(source_data.custodian, user),
    )
    if qf_result.response:
        qf_result.status, qf_result.reason_codes = _get_quotient_familial_bonus_status(user, qf_result.response.data)

    with atomic():
        if qf_result.status == subscription_models.FraudCheckStatus.KO:
            _update_quotient_familial_fraud_check_content(quotient_familial_fraud_check, qf_result)
            _decline_bonus(quotient_familial_fraud_check, qf_result)

            transactional_mails.send_bonus_declined_email(user)

        elif qf_result.status == subscription_models.FraudCheckStatus.OK:
            given_recredit = _grant_bonus(quotient_familial_fraud_check)

            if given_recredit:
                trigger_events.track_has_received_bonus(user.id)
                transactional_mails.send_bonus_granted_email(user)

        else:
            raise NotImplementedError(f"no handler was implemented for {qf_result.status}")

        external_attributes_api.update_external_user(user)


def _get_user_quotient_familial_response(
    custodian: bonus_schemas.BonusCreditPerson, user: users_models.User
) -> api_particulier.QuotientFamilialResponse:
    """
    Calls the Quotient Familial API twelve times, returning the lowest one.
    """
    birth_date = user.validatedBirthDate
    if not birth_date:
        raise ValueError("Beneficiaries applying for the bonus are expected to have a non-null birth date")

    seventeenth_birthday = birth_date + relativedelta(years=17)

    MONTHS_IN_A_YEAR = 12
    api_particulier_cutoff_date = datetime.date.today() - relativedelta(years=2)
    cutoff_month = api_particulier_cutoff_date.replace(month=1, day=1)
    all_quotient_familial_responses: list[api_particulier.QuotientFamilialResponse] = []
    for month_offset in range(MONTHS_IN_A_YEAR):
        at_date = seventeenth_birthday + relativedelta(months=month_offset)
        if at_date < cutoff_month:
            continue

        if settings.ENABLE_PARTICULIER_API_MOCK:
            quotient_familial_at_date = staging_api.get_and_mock_quotient_familial(custodian, at_date, user)
        else:
            quotient_familial_at_date = api_particulier.get_quotient_familial(custodian, at_date)

        all_quotient_familial_responses.append(quotient_familial_at_date)

    quotients_familial_with_user = [
        qf
        for qf in all_quotient_familial_responses
        if _is_user_part_of_tax_household(user, qf.data.enfants, qf.data.allocataires)
    ]
    if quotients_familial_with_user:
        relevant_qf_responses = quotients_familial_with_user
    else:
        # we store the quotient familial even if the user does not seem to belong to the tax household,
        # to allow the support department to have the last say if the identity matching algorithm fails
        relevant_qf_responses = all_quotient_familial_responses

    lowest_quotient_familial = min(relevant_qf_responses, key=lambda qf: qf.data.quotient_familial.valeur)
    return lowest_quotient_familial


def _is_user_part_of_tax_household(
    user: users_models.User,
    tax_household_children: list[api_particulier.ApiParticulierPerson],
    tax_householders: list[api_particulier.ApiParticulierPerson],
) -> bool:
    for child in tax_household_children:
        if _does_user_match_person(user, child):
            return True

    for householder in tax_householders:
        if _does_user_match_person(user, householder):
            return True

    return False


def _does_names_match(name_1: str | None, name_2: str | None) -> bool:
    if name_1 is None or name_2 is None:
        return False
    return clean_accents(name_1).upper() in clean_accents(name_2).upper()


def _does_user_match_person(user: users_models.User, person: api_particulier.ApiParticulierPerson) -> bool:
    has_first_name_match = _does_names_match(user.firstName, person.prenoms)
    has_last_name_match = _does_names_match(user.lastName, person.nom_naissance) or _does_names_match(
        user.lastName, person.nom_usage
    )
    has_birth_day_match = user.validatedBirthDate == person.date_naissance
    has_gender_match = user.gender == person.sexe

    return has_first_name_match and has_last_name_match and has_birth_day_match and has_gender_match


def _get_quotient_familial_bonus_status(
    user: users_models.User, quotient_familial_data: api_particulier.QuotientFamilialData
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode]]:
    if not _is_user_part_of_tax_household(user, quotient_familial_data.enfants, quotient_familial_data.allocataires):
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.NOT_IN_TAX_HOUSEHOLD]

    if quotient_familial_data.quotient_familial.valeur > bonus_constants.QUOTIENT_FAMILIAL_THRESHOLD:
        return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.QUOTIENT_FAMILIAL_TOO_HIGH]

    return (subscription_models.FraudCheckStatus.OK, [])


def _update_quotient_familial_fraud_check_content(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    qf_result: _ApiParticulierResult[api_particulier.QuotientFamilialResponse],
) -> None:
    quotient_familial_data = qf_result.response.data if qf_result.response else None
    if not quotient_familial_data:
        return

    if not fraud_check.resultContent:
        fraud_check.resultContent = {}

    if not fraud_check.resultContent.get("quotient_familial"):
        fraud_check.resultContent["quotient_familial"] = {}

    quotient_familial_content = bonus_schemas.QuotientFamilialContent.from_api_particulier_quotient_familial(
        quotient_familial_data.quotient_familial
    )
    fraud_check.resultContent["quotient_familial"].update(**quotient_familial_content.model_dump())

    tax_household_children = [
        bonus_schemas.BonusCreditPerson.from_api_particulier_person(child) for child in quotient_familial_data.enfants
    ]
    fraud_check.resultContent["children"] = [child.model_dump() for child in tax_household_children]

    tax_householders = [
        bonus_schemas.BonusCreditPerson.from_api_particulier_person(householder)
        for householder in quotient_familial_data.allocataires
    ]
    fraud_check.resultContent["householders"] = [householder.model_dump() for householder in tax_householders]


def apply_for_adult_disability_bonus(aah_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    """
    Checks eligibility to either the adult disability allowance (AAH).

    The handling of the user health information must be very delicate to implement GDPR regulations, to avoid leaking
    the info in any ways possible: through our own database leaks, or through external providers leaks like logging,
    monitoring or email services.

    Refer to the ADR about degraded implementation of health information if needed.
    """
    user = aah_fraud_check.user
    if not deposit_api.can_receive_bonus_credit(user):
        logger.warning("trying to apply for bonus when not able to receive said bonus")
        return

    source_data = aah_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.AdultDisabilityBonusCreditContent):
        raise ValueError(f"AdultDisabilityBonusCreditContent was expected while {type(source_data)} was given")

    if settings.ENABLE_PARTICULIER_API_MOCK:
        aah_result = _call_api_particulier(
            aah_fraud_check, lambda: staging_api.get_and_mock_disabled_adult_allowance(source_data.person, user)
        )
    else:
        aah_result = _call_api_particulier(
            aah_fraud_check, lambda: api_particulier.get_disabled_adult_allowance(source_data.person)
        )

    if aah_result.response:
        aah_result.status, aah_result.reason_codes = _get_adult_disability_bonus_status(aah_result.response.data)

    with atomic():
        if aah_result.status == subscription_models.FraudCheckStatus.KO:
            _decline_bonus(aah_fraud_check, aah_result)

        elif aah_result.status == subscription_models.FraudCheckStatus.OK:
            given_recredit = _grant_bonus(aah_fraud_check)

            if given_recredit:
                trigger_events.track_has_received_bonus(user.id)
                transactional_mails.send_bonus_granted_email(user)

        else:
            raise NotImplementedError(f"no handler was implemented for {aah_result.status}")

        external_attributes_api.update_external_user(user)


def _get_adult_disability_bonus_status(
    aah_data: api_particulier.DisabledAdultAllowanceData,
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode]]:
    if aah_data.est_beneficiaire:
        return subscription_models.FraudCheckStatus.OK, []

    return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.NOT_ELIGIBLE]


def apply_for_disabled_child_education_bonus(aeeh_fraud_check: subscription_models.BeneficiaryFraudCheck) -> None:
    """
    Checks eligibility to either the disabled child education allowance (AEEH).

    The handling of the user health information must be very delicate to implement GDPR regulations, to avoid leaking
    the info in any ways possible: through our own database leaks, or through external providers leaks like logging,
    monitoring or email services.

    Refer to the ADR about degraded implementation of health information if needed.
    """
    user = aeeh_fraud_check.user
    if not deposit_api.can_receive_bonus_credit(user):
        logger.warning("trying to apply for bonus when not able to receive said bonus")
        return

    source_data = aeeh_fraud_check.source_data()
    if not isinstance(source_data, bonus_schemas.DisabledChildEducationBonusCreditContent):
        raise ValueError(f"DisabledChildEducationBonusCreditContent was expected while {type(source_data)} was given")

    if settings.ENABLE_PARTICULIER_API_MOCK:
        aeeh_result = _call_api_particulier(
            aeeh_fraud_check,
            lambda: staging_api.get_and_mock_disabled_child_education_allowance(source_data.person, user),
        )
    else:
        aeeh_result = _call_api_particulier(
            aeeh_fraud_check, lambda: api_particulier.get_disabled_child_education_allowance(source_data.person)
        )

    if aeeh_result.response:
        aeeh_result.status, aeeh_result.reason_codes = _get_disabled_child_education_bonus_status(
            aeeh_result.response.data
        )

    with atomic():
        if aeeh_result.status == subscription_models.FraudCheckStatus.KO:
            _decline_bonus(aeeh_fraud_check, aeeh_result)

        elif aeeh_result.status == subscription_models.FraudCheckStatus.OK:
            given_recredit = _grant_bonus(aeeh_fraud_check)

            if given_recredit:
                trigger_events.track_has_received_bonus(user.id)
                transactional_mails.send_bonus_granted_email(user)

        else:
            raise NotImplementedError(f"no handler was implemented for {aeeh_result.status}")

        external_attributes_api.update_external_user(user)


def _get_disabled_child_education_bonus_status(
    aeeh_data: api_particulier.DisabledChildEducationAllowanceData,
) -> tuple[subscription_models.FraudCheckStatus, list[subscription_models.FraudReasonCode]]:
    if aeeh_data.status in [
        api_particulier.DisabledChildEducationAllowanceStatus.BENEFICIARY,
        api_particulier.DisabledChildEducationAllowanceStatus.RIGHT_OPENING,
    ]:
        return subscription_models.FraudCheckStatus.OK, []
    return subscription_models.FraudCheckStatus.KO, [subscription_models.FraudReasonCode.NOT_ELIGIBLE]


def _call_api_particulier[
    ResponseT: (
        api_particulier.QuotientFamilialResponse,
        api_particulier.DisabledAdultAllowanceResponse,
        api_particulier.DisabledChildEducationAllowanceResponse,
    )
](
    fraud_check: subscription_models.BeneficiaryFraudCheck, fetch: typing.Callable[[], ResponseT]
) -> _ApiParticulierResult[ResponseT]:
    """
    Run fetch() and format the API Particulier errors into a result.
    Re-raises unexpected errors after bumping updatedAt so the recovery cron doesn't loop.
    """
    response: ResponseT | None = None
    reason_codes = []
    error_code: str | None = None

    try:
        response = fetch()
    except api_particulier.ParticulierApiApplicationNotFound as e:
        status = subscription_models.FraudCheckStatus.KO
        reason_codes = [subscription_models.FraudReasonCode.APPLICATION_NOT_FOUND]
        http_status_code, error_code = e.status_code, e.error_code
    except api_particulier.ParticulierApiPersonNotFound as e:
        status = subscription_models.FraudCheckStatus.KO
        reason_codes = [subscription_models.FraudReasonCode.PERSON_NOT_FOUND]
        http_status_code, error_code = e.status_code, e.error_code
    except api_particulier.ParticulierApiException as e:
        with atomic():
            fraud_check.updatedAt = datetime.datetime.now(tz=None)

            if not fraud_check.resultContent:
                fraud_check.resultContent = {}
            fraud_check.resultContent["http_status_code"] = e.status_code
            fraud_check.resultContent["error_code"] = e.error_code

        raise
    except Exception:
        with atomic():
            fraud_check.updatedAt = datetime.datetime.now(tz=None)

        raise

    else:
        # the caller should apply business logic to the response to know the real status
        status = subscription_models.FraudCheckStatus.SUSPICIOUS
        http_status_code = 200

    return _ApiParticulierResult(response, status, reason_codes, http_status_code, error_code)


def _decline_bonus(
    fraud_check: subscription_models.BeneficiaryFraudCheck,
    result: _ApiParticulierResult[typing.Any],
) -> None:
    fraud_check.status = result.status
    fraud_check.reasonCodes = result.reason_codes

    if not fraud_check.resultContent:
        fraud_check.resultContent = {}

    if result.http_status_code:
        fraud_check.resultContent["http_status_code"] = result.http_status_code

    if result.error_code:
        fraud_check.resultContent["error_code"] = result.error_code


def _grant_bonus(fraud_check: subscription_models.BeneficiaryFraudCheck) -> finance_models.Recredit | None:
    user = fraud_check.user
    given_recredit = deposit_api.recredit_bonus_credit(user)

    if given_recredit:
        _delete_bonus_fraud_checks(user)
    elif deposit_api.can_receive_bonus_credit(user):
        raise ValueError(f"{fraud_check=} should have led to a credit bonus")

    return given_recredit


def _delete_bonus_fraud_checks(user: users_models.User) -> None:
    """
    We delete every bonus fraud checks to avoid retro engineering which bonus credit was granted through which process
    (AAH/AEEH or QF).
    """
    bonus_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.type in subscription_models.BONUS_CREDIT_CHECK_TYPES
    ]
    for fraud_check in bonus_fraud_checks:
        db.session.delete(fraud_check)

    db.session.flush()
