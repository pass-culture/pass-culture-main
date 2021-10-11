from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected import (
    get_duplicate_beneficiary_pre_subscription_rejected_data,
)
from pcapi.core.mails.transactional.users.email_duplicate_pre_subscription_rejected import (
    get_not_eligible_beneficiary_pre_subscription_rejected_data,
)
from pcapi.core.testing import override_features


def test_make_not_eligible_beneficiary_pre_subscription_rejected_data():
    data = get_not_eligible_beneficiary_pre_subscription_rejected_data()

    assert data == {
        "Mj-TemplateID": 1619528,
        "Mj-TemplateLanguage": True,
    }


class GetDuplicateEmailRejectedTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_get_duplicate_beneficiary_pre_subscription_rejected_data_dict_when_toggle_feature_false(self):
        data = get_duplicate_beneficiary_pre_subscription_rejected_data()
        assert data == {
            "Mj-TemplateID": 1530996,
            "Mj-TemplateLanguage": True,
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_get_duplicate_beneficiary_pre_subscription_rejected_data_sendinblue_when_toggle_feature_true(self):
        data = get_duplicate_beneficiary_pre_subscription_rejected_data()
        assert data.template == TransactionalEmail.EMAIL_DUPLICATE_BENEFICIARY_PRE_SUBCRIPTION_REJECTED
