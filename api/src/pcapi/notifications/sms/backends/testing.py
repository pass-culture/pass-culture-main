from pcapi.notifications.sms import testing
from pcapi.notifications.sms.backends.logger import LoggerBackend


class TestingBackend(LoggerBackend):
    def send_transactional_sms(self, recipient: str, content: str) -> bool:
        super().send_transactional_sms(recipient, content)
        testing.requests.append(
            {
                "recipient": recipient,
                "content": content,
            }
        )
        return True
