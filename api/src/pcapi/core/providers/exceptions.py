from pcapi.core.core_exception import CoreException


class ProviderException(CoreException):
    pass


class VenueProviderException(ProviderException):
    pass


class NoPriceSpecified(VenueProviderException):
    pass


class NoMatchingAllocineTheater(VenueProviderException):
    pass


class NoCinemaProviderPivot(VenueProviderException):
    pass


class InactiveProvider(ProviderException):
    pass
