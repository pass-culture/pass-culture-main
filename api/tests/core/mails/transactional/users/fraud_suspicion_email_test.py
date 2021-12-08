import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.users.fraud_suspicion_email import send_fraud_suspicion_email
from pcapi.core.subscription.factories import BeneficiaryPreSubscriptionFactory
from pcapi.core.testing import override_features


class FraudSuspicionEmailTest:
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_send_fraud_suspicion_email(self):
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()
        send_fraud_suspicion_email(beneficiary_pre_subscription)

        assert mails_testing.outbox[0].sent_data == {
            "template": {
                "id_prod": 82,
                "id_not_prod": 24,
                "tags": ["jeunes_compte_en_cours_d_analyse"],
                "use_priority_queue": False,
            },
            "To": beneficiary_pre_subscription.email,
            "params": {},
        }

    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=False)
    def test_send_fraud_suspicion_email_sendinblue_not_activated(self):
        beneficiary_pre_subscription = BeneficiaryPreSubscriptionFactory()
        send_fraud_suspicion_email(beneficiary_pre_subscription)

        assert mails_testing.outbox[0].sent_data == {
            "To": beneficiary_pre_subscription.email,
            "FromEmail": "support@example.com",
            "Mj-TemplateID": 2905960,
            "Mj-TemplateLanguage": True,
            "Mj-campaign": "dossier-en-analyse",
        }
