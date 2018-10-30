from datetime import datetime, timedelta
from utils.date import strftime

EVENT_OR_THING_MOCK_NAMES = [
    "Anaconda",
    "Borneo",
    "D--",
    "Funky",
    "Sun",
    "Topaz"
]

EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    strftime(datetime.utcnow() + timedelta(hours=1)),
    strftime(datetime.utcnow() + timedelta(days=2)),
    strftime(datetime.utcnow() + timedelta(days=15))
]
