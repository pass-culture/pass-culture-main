from hashlib import sha1

import factory
from factory.faker import faker

from pcapi.core.factories import BaseFactory

from . import models


Fake = faker.Faker(locale="fr_FR")


class ChronicleFactory(BaseFactory):
    class Meta:
        model = models.Chronicle

    content = "A small chronicle content."
    clubType = models.ChronicleClubType.BOOK_CLUB
    productIdentifierType = models.ChronicleProductIdentifierType.EAN
    productIdentifier = Fake.ean13()
    email = factory.Sequence("chronicle-{}@example.com".format)
    externalId = factory.Sequence(lambda x: sha1(bytes(x)).hexdigest()[0:12])
