import typing


class VenueProviderException(Exception):
    pass


class ProviderNotFound(VenueProviderException):
    pass


class VenueNotFound(VenueProviderException):
    pass


class NoPriceSpecified(VenueProviderException):
    pass


class NoAllocineTheater(VenueProviderException):
    pass


class NoAllocinePivot(VenueProviderException):
    pass


class UnknownVenueToAlloCine(VenueProviderException):
    pass


class NoCinemaProviderPivot(VenueProviderException):
    pass


class ProviderWithoutApiImplementation(VenueProviderException):
    pass


class NoSiretSpecified(VenueProviderException):
    pass


class VenueSiretNotRegistered(VenueProviderException):
    def __init__(self, provider_name: str, siret: str | None, *args: typing.Any) -> None:
        self.provider_name = provider_name
        self.siret = siret
        super().__init__(*args)


class ConnexionToProviderApiFailed(VenueProviderException):
    pass


class InactiveProvider(VenueProviderException):
    pass


class UnknownProvider(VenueProviderException):
    pass


class ShowIdNotFound(VenueProviderException):
    pass
