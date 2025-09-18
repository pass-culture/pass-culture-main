from datetime import datetime

import factory.fuzzy

import pcapi.core.users.factories as users_factories
from pcapi.core import factories
from pcapi.core.fraud import models


class BlacklistedDomainNameFactory(factories.BaseFactory):
    class Meta:
        model = models.BlacklistedDomainName

    domain = factory.Sequence("my-domain-{}.com".format)


class ProductWhitelistFactory(factories.BaseFactory):
    class Meta:
        model = models.ProductWhitelist

    comment = factory.Sequence("OK {} !".format)
    title = factory.Sequence("Ducobu #{} !".format)
    ean = factory.fuzzy.FuzzyText(length=13)
    dateCreated = factory.LazyFunction(datetime.utcnow)
    author = factory.SubFactory(users_factories.AdminFactory)
