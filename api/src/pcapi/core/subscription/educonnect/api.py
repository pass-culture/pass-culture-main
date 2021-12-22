import datetime
import logging

from pcapi.core.fraud import api as fraud_api
from pcapi.core.fraud import exceptions as fraud_exceptions
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription import api as subscription_api
from pcapi.core.users import models as users_models
from pcapi.core.users.external.educonnect import models as educonnect_models
from pcapi.models.beneficiary_import import BeneficiaryImportSources

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
    except fraud_exceptions.BeneficiaryFraudResultCannotBeDowngraded:
        logger.exception("Trying to downgrade FraudResult after eduonnect response", extra={"user_id": user.id})
        raise exceptions.EduconnectSubscriptionException()
    except Exception:
        logger.exception("Error on educonnect result", extra={"user_id": user.id})
        raise exceptions.EduconnectSubscriptionException()

    if fraud_check.status == fraud_models.FraudCheckStatus.OK:
        try:
            subscription_api.on_successful_application(
                user=user,
                source=BeneficiaryImportSources.educonnect,
                source_data=fraud_check.source_data(),
                eligibility_type=fraud_api.get_eligibility_type(fraud_check.source_data()),
                third_party_id=fraud_check.thirdPartyId,
                source_id=None,
            )
        except Exception:
            logger.exception("Error while creating BeneficiaryImport from Educonnect", extra={"user_id": user.id})
            raise exceptions.EduconnectSubscriptionException()
    else:
        logger.warning(
            "Fraud suspicion after educonnect authentication with codes: %s",
            (", ").join([code.value for code in fraud_check.reasonCodes]),
            extra={"user_id": user.id},
        )

    return fraud_check.reasonCodes
