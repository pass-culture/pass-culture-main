""" event_occurrences """
from datetime import timedelta

from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS
from sandboxes.scripts.utils.generators import get_all_typed_event_occurrence_mocks
from utils.date import today, strftime
from utils.human_ids import dehumanize, humanize

EVENT_OCCURRENCE_MOCKS = []

SCRATCH_EVENT_OCCURRENCE_MOCKS = [
    {
        "beginningDatetime": strftime(today),
        "endDatetime": strftime(today + timedelta(hours=1)),
        "id": humanize(1),
        "offerId": humanize(1) # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },
    {
        "beginningDatetime": strftime(today + timedelta(days=1)),
        "endDatetime": strftime(today + timedelta(days=1, hours=1)),
        "id": humanize(2),
        "offerId": humanize(1) # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },
    {
        "beginningDatetime": strftime(today),
        "endDatetime": strftime(today + timedelta(hours=2)),
        "id": humanize(3),
        "offerId": humanize(2) # Concert de Gael Faye THEATRE DE L ODEON
    },
    {
        "beginningDatetime": strftime(today),
        "endDatetime": strftime(today + timedelta(hours=3)),
        "id": humanize(4),
        "offerId": humanize(3) # PNL chante Marx THEATRE DE L ODEON
    }
]
EVENT_OCCURRENCE_MOCKS += SCRATCH_EVENT_OCCURRENCE_MOCKS

ALL_TYPED_EVENT_OCCURRENCE_MOCKS = get_all_typed_event_occurrence_mocks(
    ALL_TYPED_EVENT_OFFER_MOCKS,
    starting_id=dehumanize(EVENT_OCCURRENCE_MOCKS[-1]['id']) + 1
)
EVENT_OCCURRENCE_MOCKS += ALL_TYPED_EVENT_OCCURRENCE_MOCKS
