""" sandbox light """
from sandboxes.scripts.mocks.bookings import BOOKING_MOCKS
from sandboxes.scripts.mocks.deposits import DEPOSIT_MOCKS
from sandboxes.scripts.mocks.events import EVENT_MOCKS
from sandboxes.scripts.mocks.event_occurrences import EVENT_OCCURRENCE_MOCKS
from sandboxes.scripts.mocks.offers import OFFER_MOCKS
from sandboxes.scripts.mocks.offerers import OFFERER_MOCKS
from sandboxes.scripts.mocks.recommendations import RECOMMENDATION_MOCKS
from sandboxes.scripts.mocks.stocks import STOCK_MOCKS
from sandboxes.scripts.mocks.things import THING_MOCKS
from sandboxes.scripts.mocks.user_offerers import USER_OFFERER_MOCKS
from sandboxes.scripts.mocks.users_webapp import USER_MOCKS
from sandboxes.scripts.mocks.venues import VENUE_MOCKS

__all__ = (
    "BOOKING_MOCKS",
    "DEPOSIT_MOCKS",
    "EVENT_MOCKS",
    "EVENT_OCCURRENCE_MOCKS",
    "OFFER_MOCKS",
    "OFFERER_MOCKS",
    "RECOMMENDATION_MOCKS",
    "STOCK_MOCKS",
    "THING_MOCKS",
    "USER_OFFERER_MOCKS",
    "USER_MOCKS",
    "VENUE_MOCKS"
)
