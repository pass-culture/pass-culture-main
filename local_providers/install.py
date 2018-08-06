""" local providers install """
import local_providers
from models.db import db
from models.provider import Provider

for name in local_providers.__all__:
    provider = getattr(local_providers, name)
    db_provider = Provider.getByClassName(name)

    if not db_provider:
        p = Provider()
        p.name = provider.name
        p.localClass = name
        p.isActive = False
        db.session.add(p)
        db.session.commit()
