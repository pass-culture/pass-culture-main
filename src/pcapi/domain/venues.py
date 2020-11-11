from typing import Dict

from pcapi.models import VenueSQLEntity
from pcapi.routes.serialization import as_dict


VENUE_ALGOLIA_INDEXED_FIELDS = ["name", "publicName", "city"]


def is_algolia_indexing(previous_venue: VenueSQLEntity, payload: Dict) -> bool:
    previous_venue_as_dict = as_dict(previous_venue)
    for field in VENUE_ALGOLIA_INDEXED_FIELDS:
        if field in payload.keys() and previous_venue_as_dict[field] != payload[field]:
            return True
    return False
