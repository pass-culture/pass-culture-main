from pcapi.connectors.beneficiaries import get_application_by_id
from pcapi.core.users.api import create_reset_password_token
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import BeneficiaryIsADuplicate
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_exceptions import CantRegisterBeneficiary
from pcapi.domain.beneficiary_pre_subscription.beneficiary_pre_subscription_validator import validate
from pcapi.domain.user_emails import send_accepted_as_beneficiary_email
from pcapi.domain.user_emails import send_activation_email
from pcapi.domain.user_emails import send_rejection_email_to_beneficiary_pre_subscription
from pcapi.infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from pcapi.repository.user_queries import find_user_by_email
from pcapi.workers.push_notification_job import update_user_attributes_job


class CreateBeneficiaryFromApplication:
    def __init__(self) -> None:
        self.beneficiary_repository = BeneficiarySQLRepository()

    def execute(self, application_id: int) -> None:
        beneficiary_pre_subscription = get_application_by_id(application_id)

        user = find_user_by_email(beneficiary_pre_subscription.email)

        try:
            validate(beneficiary_pre_subscription, preexisting_account=user)

        except CantRegisterBeneficiary as cant_register_beneficiary_exception:
            self.beneficiary_repository.reject(
                beneficiary_pre_subscription, detail=str(cant_register_beneficiary_exception)
            )
            send_rejection_email_to_beneficiary_pre_subscription(
                beneficiary_pre_subscription=beneficiary_pre_subscription,
                beneficiary_is_eligible=isinstance(cant_register_beneficiary_exception, BeneficiaryIsADuplicate),
            )

        else:
            beneficiary = self.beneficiary_repository.save(beneficiary_pre_subscription, user=user)
            if user is None:
                token = create_reset_password_token(beneficiary)
                send_activation_email(user=beneficiary, token=token)
            else:
                send_accepted_as_beneficiary_email(user=beneficiary)

            update_user_attributes_job.delay(beneficiary.id)


create_beneficiary_from_application = CreateBeneficiaryFromApplication()
