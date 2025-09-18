import dataclasses

import pcapi.core.mails.transactional.sendinblue_template_ids as sendinblue_template
import pcapi.core.subscription.models as subscription_models


@dataclasses.dataclass
class UbbleErrorToEmailMapping:
    template: sendinblue_template.TransactionalEmail
    reminder_template: sendinblue_template.TransactionalEmail


default_email = UbbleErrorToEmailMapping(
    template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_UNREADABLE_DOCUMENT_ERROR,
    reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_UNPROCESSABLE,
)

ubble_error_to_email_mapping = {
    subscription_models.FraudReasonCode.ID_CHECK_DATA_MATCH.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_INFORMATION_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_DATA_MATCH,
    ),
    subscription_models.FraudReasonCode.ID_CHECK_BLOCKED_OTHER.value: default_email,
    subscription_models.FraudReasonCode.ID_CHECK_UNPROCESSABLE.value: default_email,
    subscription_models.FraudReasonCode.ID_CHECK_NOT_SUPPORTED.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_FOREIGN_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_SUPPORTED,
    ),
    subscription_models.FraudReasonCode.ID_CHECK_EXPIRED.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_INVALID_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_EXPIRED,
    ),
    subscription_models.FraudReasonCode.ID_CHECK_NOT_AUTHENTIC.value: UbbleErrorToEmailMapping(
        template=sendinblue_template.TransactionalEmail.SUBSCRIPTION_NOT_AUTHENTIC_DOCUMENT_ERROR,
        reminder_template=sendinblue_template.TransactionalEmail.UBBLE_KO_REMINDER_ID_CHECK_NOT_AUTHENTIC,
    ),
}
