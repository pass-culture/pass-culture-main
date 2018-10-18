""" sandbox light """
from sandboxes.scripts.mocks.bookings import booking_mocks
from sandboxes.scripts.mocks.deposits import deposit_mocks
from sandboxes.scripts.mocks.events import event_mocks
from sandboxes.scripts.mocks.event_occurrences import event_occurrence_mocks
from sandboxes.scripts.mocks.offers import offer_mocks
from sandboxes.scripts.mocks.offerers import offerer_mocks
from sandboxes.scripts.mocks.recommendations import recommendation_mocks
from sandboxes.scripts.mocks.stocks import stock_mocks
from sandboxes.scripts.mocks.things import thing_mocks
from sandboxes.scripts.mocks.user_offerers import user_offerer_mocks
from sandboxes.scripts.mocks.users_light import user_mocks
from sandboxes.scripts.mocks.venues import venue_mocks

__all__ = (
    "booking_mocks",
    "deposit_mocks",
    "event_mocks",
    "event_occurrence_mocks",
    "offer_mocks",
    "offerer_mocks",
    "recommendation_mocks",
    "stock_mocks",
    "thing_mocks",
    "user_offerer_mocks",
    "user_mocks",
    "venue_mocks"
)
