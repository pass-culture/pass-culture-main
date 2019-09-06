from datetime import datetime

from models.db import Model


class ProvidableInfo(object):
    type = Model
    id_at_providers = ''
    date_modified_at_provider = datetime(1900, 1, 1)
