from .adage_playlists import (
    ClassroomPlaylistQuery,  # noqa: F401
    InstitutionRuralLevelQuery,  # noqa: F401
    LocalOfferersQuery,  # noqa: F401
    NewOffererQuery,  # noqa: F401
    NewTemplateOffersPlaylistQuery,  # noqa: F401
)
from .artist import (
    ArtistAliasQuery,  # noqa: F401
    ArtistProductLinkQuery,  # noqa: F401
    ArtistQuery,  # noqa: F401
)
from .favorites_not_booked import (
    FavoritesNotBooked,  # noqa: F401
    FavoritesNotBookedModel,  # noqa: F401
)
from .last_30_days_booking import Last30DaysBookings  # noqa: F401
from .marketing import ProLiveShowEmailChurned40DaysAgoQuery, ProLiveShowEmailLastBooking40DaysAgoQuery
from .pro_email_churned_40_days_ago import ChurnedProEmail  # noqa: F401
from .pro_no_bookings_since_40_days_ago import NoBookingsProEmail  # noqa: F401
