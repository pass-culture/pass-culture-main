from hashlib import sha1

import factory

from pcapi.core.factories import BaseFactory

from . import models


class ChronicleFactory(BaseFactory):
    class Meta:
        model = models.Chronicle

    content = "A small chronicle content."
    email = factory.Sequence("chronicle-{}@example.com".format)
    externalId = factory.Sequence(lambda x: sha1(bytes(x)).hexdigest()[0:12])
