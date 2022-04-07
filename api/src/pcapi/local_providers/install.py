from pcapi import settings
from pcapi.core.providers.models import Provider
from pcapi.core.providers.repository import get_provider_by_local_class
import pcapi.local_providers
from pcapi.models import db


def install_local_providers():  # type: ignore [no-untyped-def]
    # It is a lot easier in tests when all providers are active by
    # default (and manually inactivated if a particular test needs
    # that).
    activate_and_enable_for_pro = settings.IS_RUNNING_TESTS
    for class_name in pcapi.local_providers.__all__:
        provider_class = getattr(pcapi.local_providers, class_name)
        db_provider = get_provider_by_local_class(class_name)

        if not db_provider:
            provider = Provider()
            provider.name = provider_class.name
            provider.localClass = class_name
            provider.isActive = activate_and_enable_for_pro
            provider.enabledForPro = activate_and_enable_for_pro
            db.session.add(provider)

    db.session.commit()
