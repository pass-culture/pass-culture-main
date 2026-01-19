from pcapi.core.core_exception import CoreException


class ArtistException(CoreException):
    pass


class MissingArtistDataException(ArtistException):
    def __init__(self) -> None:
        super().__init__({"artistOfferLinks": ["An artist offer link must have either an artist_id or a custom_name"]})


class DuplicateArtistException(ArtistException):
    def __init__(self) -> None:
        super().__init__({"artistOfferLinks": ["An artist can only be linked once per type"]})


class DuplicateCustomArtistException(ArtistException):
    def __init__(self) -> None:
        super().__init__({"artistOfferLinks": ["A custom name can only be linked once per type"]})


class InvalidArtistDataException(ArtistException):
    def __init__(self) -> None:
        super().__init__({"artistOfferLinks": ["Invalid artist id"]})
