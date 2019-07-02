""" local providers install """
import local_providers
from models.db import db
from models.provider import Provider
from repository.provider_queries import get_provider_by_local_class


def install_local_providers():
    for class_name in local_providers.__all__:
        provider_class = getattr(local_providers, class_name)
        db_provider = get_provider_by_local_class(class_name)

        if not db_provider:
            provider = Provider()
            provider.name = provider_class.name
            provider.localClass = class_name
            provider.isActive = False
            db.session.add(provider)

    db.session.commit()

