import logging

from pcapi.connectors.beneficiaries import get_application_by_id
from pcapi.core.users.api import create_reset_password_token
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import BeneficiaryIsADuplicate
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import CantRegisterBeneficiary
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import FraudDetected
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import SuspiciousFraudDetected
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_fraud_validator import validate_fraud
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_validator import validate
from pcapi.domain.user_emails import send_accepted_as_beneficiary_email
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription
from pcapi.infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.workers.push_notification_job import update_user_attributes_job


logger = logging.getLogger(__name__)


class CreateBeneficiaryFromApplication:
    def __init__(self) -> None:
        self.beneficiary_repository = BeneficiarySQLRepository()

    def execute(self, application_id: int, run_fraud_detection: bool = True, fraud_detection_ko: bool = False) -> None:
        beneficiary_pre_subscription = get_application_by_id(application_id)
        preexisting_account = find_user_by_email(beneficiary_pre_subscription.email)

        try:
            validate(beneficiary_pre_subscription, preexisting_account=preexisting_account)
            if fraud_detection_ko:
                raise FraudDetected("Forced by 'fraud_detection_ko' script argument")
            if run_fraud_detection:
                validate_fraud(beneficiary_pre_subscription)

        except SuspiciousFraudDetected:
            pass
        except FraudDetected as cant_register_beneficiary_exception:
            # detail column cannot contain more than 255 characters
            detail = f"Fraud controls triggered: {cant_register_beneficiary_exception}"[:255]
            self.beneficiary_repository.reject(
                beneficiary_pre_subscription,
                detail=detail,
                user=preexisting_account,
            )
        except CantRegisterBeneficiary as cant_register_beneficiary_exception:
            logger.warning("Couldn't register user from application", extra={"applicationId": application_id})
            self.beneficiary_repository.reject(
                beneficiary_pre_subscription, detail=str(cant_register_beneficiary_exception), user=preexisting_account
            )
            send_rejection_email_to_beneficiary_pre_subscription(
                beneficiary_pre_subscription=beneficiary_pre_subscription,
                beneficiary_is_eligible=isinstance(cant_register_beneficiary_exception, BeneficiaryIsADuplicate),
            )
        else:
            user = self.beneficiary_repository.save(beneficiary_pre_subscription, user=preexisting_account)
            logger.info("User registered from application", extra={"applicationId": application_id, "userId": user.id})

            if preexisting_account is None:
                token = create_reset_password_token(user)
                send_activation_email(user=user, token=token)
            else:
                send_accepted_as_beneficiary_email(user=user)

            update_user_attributes_job.delay(user.id)


create_beneficiary_from_application = CreateBeneficiaryFromApplication()
