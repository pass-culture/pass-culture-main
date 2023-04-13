from pcapi import settings
from pcapi.core.external.backends.base import BaseBackend
from pcapi.utils.module_loading import import_string


zendesk_backend: BaseBackend = import_string(settings.ZENDESK_SELL_BACKEND)()
