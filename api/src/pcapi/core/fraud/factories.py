import factory.fuzzy

import pcapi.core.users.factories as users_factories
from pcapi.core import factories
from pcapi.core.fraud import models
from pcapi.utils import date as date_utils


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
    dateCreated = factory.LazyFunction(date_utils.get_naive_utc_now)
    author = factory.SubFactory(users_factories.AdminFactory)
