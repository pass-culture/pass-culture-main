import logging


logger = logging.getLogger(__name__)


class SlackBackend:
    def __init__(self):
        pass

    def send_internal_message(self, recipient: str, content: str) -> bool:
        pass
