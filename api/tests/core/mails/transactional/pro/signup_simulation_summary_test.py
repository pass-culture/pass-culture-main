from dataclasses import asdict

from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional import send_signup_simulation_summary_email
from pcapi.core.mails.transactional.brevo_template_ids import TransactionalEmail
from pcapi.core.offerers.structure_signup_api import EligibilityDocument


class SignupSimulationSummaryTest:
    def test_send_mail(self):
        email = "bloup@example.fr"
        link = "my-signup-link.com"
        documents = [EligibilityDocument.WEBSITE, EligibilityDocument.DIPLOMAS]

        send_signup_simulation_summary_email(
            email=email,
            signup_link="my-signup-link.com",
            eligibility_documents=documents,
        )

        assert len(mails_testing.outbox) == 1

        assert mails_testing.outbox[0]["template"] == asdict(TransactionalEmail.SIGNUP_SIMULATION_SUMMARY.value)
        assert mails_testing.outbox[0]["To"] == email
        assert mails_testing.outbox[0]["params"]["SIGNUP_LINK"] == link
        assert mails_testing.outbox[0]["params"]["ELIGIBILITY_DOCUMENTS"] == ["WEBSITE", "DIPLOMAS"]
