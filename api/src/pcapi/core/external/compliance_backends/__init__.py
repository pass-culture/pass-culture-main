from pcapi import settings
from pcapi.core.external.compliance_backends.base import BaseBackend
from pcapi.utils.module_loading import import_string


compliance_backend: BaseBackend = import_string(settings.COMPLIANCE_BACKEND)()
