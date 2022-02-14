# FIXME: move these exceptions to `core.offerers.exceptions`?
class AdageException(Exception):
    def __init__(self, message, status_code, response_text):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(message)


class CulturalPartnerNotFoundException(Exception):
    pass
