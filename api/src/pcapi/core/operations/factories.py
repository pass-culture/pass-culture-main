import datetime
import uuid

import factory.fuzzy

from pcapi.core.factories import BaseFactory
from pcapi.core.users import factories as users_factories

from . import models


class SpecialEventFactory(BaseFactory):
    class Meta:
        model = models.SpecialEvent

    externalId = factory.Sequence("ExtIdEvt{:04}".format)
    dateCreated = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=2))
    title = factory.Sequence("Opération #{}".format)
    eventDate = factory.LazyFunction(lambda: datetime.date.today() + datetime.timedelta(days=7))


class SpecialEventQuestionFactory(BaseFactory):
    class Meta:
        model = models.SpecialEventQuestion

    event = factory.SubFactory(SpecialEventFactory)
    externalId = factory.Sequence("ExtIdQst{:04}".format)
    title = factory.Sequence("Question #{}".format)


class SpecialEventResponseFactory(BaseFactory):
    class Meta:
        model = models.SpecialEventResponse

    event = factory.SubFactory(SpecialEventFactory)
    externalId = factory.Sequence("ExtIdRes{:04}".format)
    dateSubmitted = factory.LazyFunction(lambda: datetime.datetime.utcnow() - datetime.timedelta(days=1))
    user: factory.declarations.BaseDeclaration | None = factory.SubFactory(users_factories.BeneficiaryFactory)
    phoneNumber: factory.declarations.BaseDeclaration | str | None = factory.SelfAttribute("user.phoneNumber")
    email: factory.declarations.BaseDeclaration = factory.SelfAttribute("user.email")
    status = models.SpecialEventResponseStatus.NEW


class SpecialEventResponseNoUserFactory(SpecialEventResponseFactory):
    class Meta:
        model = models.SpecialEventResponse

    user = None
    phoneNumber = "0012345678"
    email = factory.LazyFunction(lambda: f"non.inscrit_{uuid.uuid4()}@example.com")


class SpecialEventAnswerFactory(BaseFactory):
    class Meta:
        model = models.SpecialEventAnswer

    responseId = factory.SubFactory(SpecialEventResponseFactory)
    questionId = factory.SubFactory(SpecialEventQuestionFactory)
    text = factory.Sequence("Réponse #{}".format)
