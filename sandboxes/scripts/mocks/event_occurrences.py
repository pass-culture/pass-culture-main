""" event_occurrences """
from datetime import timedelta

from sandboxes.scripts.mocks.offers import ALL_TYPED_EVENT_OFFER_MOCKS
from sandboxes.scripts.mocks.utils.generators import get_all_typed_event_occurrence_mocks
from utils.date import today, strftime
from utils.human_ids import humanize

EVENT_OCCURRENCE_MOCKS = []

ALL_TYPED_EVENT_OCCURRENCE_MOCKS = get_all_typed_event_occurrence_mocks(ALL_TYPED_EVENT_OFFER_MOCKS)
EVENT_OCCURRENCE_MOCKS += ALL_TYPED_EVENT_OCCURRENCE_MOCKS

SCRATCH_EVENT_OCCURRENCE_MOCKS = [
    {
        "beginningDatetime": strftime(today),
        "id": humanize(0),
        "offerId": humanize(0) # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },
    {
        "beginningDatetime": strftime(today + timedelta(days=1)),
        "id": humanize(1),
        "offerId": humanize(0) # Rencontre avec Franck Lepage  LE GRAND REX PARIS
    },
    {
        "beginningDatetime": strftime(today),
        "id": humanize(2),
        "offerId": humanize(1) # Concert de Gael Faye THEATRE DE L ODEON
    },
    {
        "beginningDatetime": strftime(today),
        "id": humanize(3),
        "offerId": humanize(2) # PNL chante Marx THEATRE DE L ODEON
    }
]
EVENT_OCCURRENCE_MOCKS += SCRATCH_EVENT_OCCURRENCE_MOCKS
