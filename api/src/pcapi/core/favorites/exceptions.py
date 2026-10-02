from pcapi.core.core_exception import CoreException


class FavoriteException(CoreException):
    pass


class UnhandledFavoriteType(FavoriteException):
    pass


class MaxFavoritesReached(FavoriteException):
    pass


class InactiveOffer(FavoriteException):
    pass


class FavoriteNotFound(FavoriteException):
    pass


class AlreadyAsFavorite(FavoriteException):
    pass
