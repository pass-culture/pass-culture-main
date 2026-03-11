from pcapi.core.subscription.phone_validation.sms import testing
from pcapi.core.subscription.phone_validation.sms.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def send_transactional_sms(self, recipient: str, content: str) -> None:
        super().send_transactional_sms(recipient, content)
        testing.requests.append(
            {
                "recipient": recipient,
                "content": content,
            }
        )
