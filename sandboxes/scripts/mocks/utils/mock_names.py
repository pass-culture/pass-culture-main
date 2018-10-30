from datetime import datetime, timedelta
from sandboxes.scripts.mocks import read_json_date

EVENT_OR_THING_MOCK_NAMES = [
    "Anaconda",
    "Borneo",
    "D--",
    "Funky",
    "Sun",
    "Topaz"
]

EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    read_json_date(datetime.utcnow() + timedelta(hours=1)),
    read_json_date(datetime.utcnow() + timedelta(days=2)),
    read_json_date(datetime.utcnow() + timedelta(days=15))
]
