from pcapi.core.core_exception import CoreException


class ProviderException(CoreException):
    pass


class VenueProviderException(Exception):
    pass


class NoPriceSpecified(VenueProviderException):
    pass


class UnknownVenueToAlloCine(VenueProviderException):
    pass


class NoCinemaProviderPivot(VenueProviderException):
    pass


class InactiveProvider(VenueProviderException):
    pass
