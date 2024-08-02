from pcapi import settings
from pcapi.core.external.subcategory_suggestion_backends.base import BaseBackend
from pcapi.utils.module_loading import import_string


subcategory_suggestion_backend: BaseBackend = import_string(settings.SUBCATEGORY_SUGGESTION_BACKEND)()
