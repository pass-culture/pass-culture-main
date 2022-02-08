import datetime
import logging

from pcapi.connectors.beneficiaries.educonnect import models as educonnect_models
from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.subscription import messages as subscription_messages
from pcapi.core.users import api as users_api
from pcapi.core.users import constants as users_constants
from pcapi.core.users import models as users_models

from . import exceptions


logger = logging.getLogger(__name__)


def handle_educonnect_authentication(
    user: users_models.User, educonnect_user: educonnect_models.EduconnectUser
) -> list[fraud_models.FraudReasonCode]:
    educonnect_content = fraud_models.EduconnectContent(
        birth_date=educonnect_user.birth_date,
        educonnect_id=educonnect_user.educonnect_id,
        first_name=educonnect_user.first_name,
        ine_hash=educonnect_user.ine_hash,
        last_name=educonnect_user.last_name,
        registration_datetime=datetime.datetime.now(),
        school_uai=educonnect_user.school_uai,
        student_level=educonnect_user.student_level,
    )

    try:
        fraud_check = fraud_api.on_educonnect_result(user, educonnect_content)
    except Exception:
        logger.exception("Error on educonnect result", extra={"user_id": user.id})
        raise exceptions.EduconnectSubscriptionException()

    if fraud_check.status == fraud_models.FraudCheckStatus.OK:
        try:
            subscription_api.on_successful_application(user=user, source_data=fraud_check.source_data())
        except Exception:
            logger.exception("Error while creating BeneficiaryImport from Educonnect", extra={"user_id": user.id})
            raise exceptions.EduconnectSubscriptionException()
    else:
        _add_error_subscription_messages(user, fraud_check.reasonCodes, educonnect_user)
        subscription_api.update_user_birth_date(user, fraud_check.source_data().get_birth_date())
        logger.warning(
            "Fraud suspicion after educonnect authentication with codes: %s",
            (", ").join([code.value for code in fraud_check.reasonCodes]),
            extra={"user_id": user.id},
        )

    return fraud_check.reasonCodes


def _add_error_subscription_messages(
    user: users_models.User,
    reason_codes: list[fraud_models.FraudReasonCode],
    educonnect_user: educonnect_models.EduconnectUser,
) -> None:
    if fraud_models.FraudReasonCode.ALREADY_BENEFICIARY in reason_codes:
        subscription_messages.on_already_beneficiary(user)

    if fraud_models.FraudReasonCode.AGE_NOT_VALID in reason_codes:
        message = f"Ton dossier a été refusé. La date de naissance enregistrée sur ton compte Educonnect ({educonnect_user.birth_date.strftime('%d/%m/%Y')}) indique que tu n'as pas entre {users_constants.ELIGIBILITY_UNDERAGE_RANGE[0]} et {users_constants.ELIGIBILITY_UNDERAGE_RANGE[-1]} ans."
        subscription_messages.add_error_message(user, message)

    elif fraud_models.FraudReasonCode.NOT_ELIGIBLE in reason_codes:
        message = f"La date de naissance de ton dossier Educonnect ({educonnect_user.birth_date.strftime('%d/%m/%Y')}) indique que tu n'es pas éligible."
        eligibity_start = users_api.get_eligibility_start_datetime(educonnect_user.birth_date)

        if datetime.datetime.now() < eligibity_start:
            message += f" Tu seras éligible le {eligibity_start.strftime('%d/%m/%Y')}."

        subscription_messages.add_error_message(user, message)

    if fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        subscription_messages.add_error_message(
            user,
            "Ton compte ÉduConnect est déjà rattaché à un autre compte pass Culture. Vérifie que tu n'as pas déjà créé un compte avec une autre adresse mail.",
        )

    if fraud_models.FraudReasonCode.DUPLICATE_USER in reason_codes:
        subscription_messages.add_error_message(
            user,
            "Ton identificant national INE est déjà rattaché à un autre compte pass Culture. Vérifie que tu n'as pas déjà créé un compte avec une autre adresse mail.",
        )

    if fraud_models.FraudReasonCode.INE_NOT_WHITELISTED in reason_codes:
        message = (
            "Tu ne fais pas partie de la phase de test. Encore un peu de patience, on se donne rendez-vous en janvier."
        )
        subscription_messages.add_error_message(user, message)
