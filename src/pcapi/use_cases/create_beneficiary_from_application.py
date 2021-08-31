import logging

from pcapi.connectors.beneficiaries import jouve_backend
from pcapi.core.fraud.api import on_jouve_result
from pcapi.core.users.api import create_reset_password_token
from pcapi.core.users.external import update_external_user
from pcapi.domain.beneficiary_pre_subscription.exceptions import BeneficiaryIsADuplicate
from pcapi.domain.beneficiary_pre_subscription.exceptions import CantRegisterBeneficiary
from pcapi.domain.beneficiary_pre_subscription.exceptions import FraudDetected
from pcapi.domain.beneficiary_pre_subscription.exceptions import SuspiciousFraudDetected
from pcapi.domain.beneficiary_pre_subscription.fraud_validator import validate_fraud
from pcapi.domain.beneficiary_pre_subscription.validator import validate
from pcapi.domain.user_emails import send_accepted_as_beneficiary_email
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_fraud_suspicion_email
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription
from pcapi.infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from pcapi.repository.user_queries import find_user_by_email


logger = logging.getLogger(__name__)


class CreateBeneficiaryFromApplication:
    def __init__(self) -> None:
        self.beneficiary_repository = BeneficiarySQLRepository()

    def execute(
        self,
        application_id: int,
        run_fraud_detection: bool = True,
        ignore_id_piece_number_field: bool = False,
        fraud_detection_ko: bool = False,
    ) -> None:
        try:
            jouve_content = jouve_backend.get_application_content(
                application_id, ignore_id_piece_number_field=ignore_id_piece_number_field
            )
            beneficiary_pre_subscription = jouve_backend.get_subscription_from_content(jouve_content)
        except jouve_backend.ApiJouveException as api_jouve_exception:
            logger.error(
                api_jouve_exception.message,
                extra={
                    "route": api_jouve_exception.route,
                    "statusCode": api_jouve_exception.status_code,
                    "applicationId": application_id,
                },
            )
            return
        except jouve_backend.JouveContentValidationError as exc:
            logger.error(
                "Validation error when parsing Jouve content: %s",
                exc.message,
                extra={"application_id": application_id, "validation_errors": exc.errors},
            )
            return

        preexisting_account = find_user_by_email(beneficiary_pre_subscription.email)
        if preexisting_account:
            try:
                on_jouve_result(preexisting_account, jouve_content)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Error on jouve result: %s", exc)

        try:
            validate(
                beneficiary_pre_subscription,
                preexisting_account=preexisting_account,
                ignore_id_piece_number_field=ignore_id_piece_number_field,
            )
            if fraud_detection_ko:
                raise FraudDetected("Forced by 'fraud_detection_ko' script argument")
            if run_fraud_detection:
                validate_fraud(beneficiary_pre_subscription)

        except SuspiciousFraudDetected:
            send_fraud_suspicion_email(beneficiary_pre_subscription)
        except FraudDetected as cant_register_beneficiary_exception:
            # detail column cannot contain more than 255 characters
            detail = f"Fraud controls triggered: {cant_register_beneficiary_exception}"[:255]
            self.beneficiary_repository.reject(
                beneficiary_pre_subscription,
                detail=detail,
                user=preexisting_account,
            )
        except CantRegisterBeneficiary as cant_register_beneficiary_exception:
            exception_reason = str(cant_register_beneficiary_exception)
            logger.warning(
                "Couldn't register user from application",
                extra={
                    "applicationId": application_id,
                    "reason": exception_reason,
                },
            )
            self.beneficiary_repository.reject(
                beneficiary_pre_subscription, detail=exception_reason, user=preexisting_account
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

            update_external_user(user)


create_beneficiary_from_application = CreateBeneficiaryFromApplication()
