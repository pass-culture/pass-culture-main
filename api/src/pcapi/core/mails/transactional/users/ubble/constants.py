import dataclasses

import pcapi.core.fraud.models as fraud_models
import pcapi.core.mails.transactional.sendinblue_template_ids as sendinblue_template


@dataclasses.dataclass
class UbbleErrorToEmailMapping:
    template: sendinblue_template.TransactionalEmail
    reminder_template: sendinblue_template.TransactionalEmail | None = None


ubble_error_to_email_mapping = {
    fraud_models.FraudReasonCode.ID_CHECK_DATA_MATCH.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_DATA_MATCH,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_EXPIRED.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_EXPIRED,
    ),
    fraud_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_NOT_AUTHENTIC_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC,
    ),
}
