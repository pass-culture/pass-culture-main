from datetime import datetime

from pcapi.models.db import Model


class ProvidableInfo:
    type = Model
    id_at_providers = ""
    new_id_at_provider = ""
    date_modified_at_provider = datetime(1900, 1, 1)
