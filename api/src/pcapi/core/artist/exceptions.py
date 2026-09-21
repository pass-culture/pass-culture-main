from pcapi.core.core_exception import CoreException


class ArtistException(CoreException):
    def __init__(self, message: str):
        self.message = message
        super().__init__()
