import datetime
import random

import factory

from pcapi.core import testing
import pcapi.core.users.factories as users_factories

from . import models


class BeneficiaryPreSubscriptionFactory(factory.Factory):
    class Meta:
        model = models.BeneficiaryPreSubscription

    date_of_birth = datetime.datetime(1995, 2, 5)
    activity: str = "Apprenti"
    address: str = "3 rue de Valois"
    application_id: str = "12"
    city: str = "Paris"
    postal_code: str = "35123"
    email: str = "rennes@example.org"
    first_name: str = "Thomas"
    civility: str = "Mme"
    last_name: str = "DURAND"
    phone_number: str = "0123456789"
    source: str = "jouve"
    source_id: str = None
    id_piece_number: str = "140767100016"
    fraud_fields = factory.LazyAttribute(lambda x: [])


class SubscriptionMessageFactory(testing.BaseFactory):
    class Meta:
        model = models.SubscriptionMessage

    user = factory.SubFactory(users_factories.UserFactory)
    userMessage = factory.Faker("sentence", nb_words=3)
    callToActionTitle = factory.Sequence("Call To Action title #{0}".format)
    callToActionLink = factory.Sequence("https://ctalink.example.com/{0}".format)
    callToActionIcon = factory.LazyAttribute(lambda o: random.choice(list(models.CallToActionIcon)))
    popOverIcon = factory.LazyAttribute(lambda o: random.choice(list(models.PopOverIcon)))
