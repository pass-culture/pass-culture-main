import factory

from pcapi.core.factories import BaseFactory

from . import models


class ChronicleFactory(BaseFactory):
    class Meta:
        model = models.Chronicle

    content = "A small chronicle content."
    email = factory.Sequence("chronicle-{}@example.com".format)
    formId = "54c77f43519a"
