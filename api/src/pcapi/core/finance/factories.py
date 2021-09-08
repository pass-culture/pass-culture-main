import factory
from factory.declarations import LazyAttribute

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.testing import BaseFactory

from . import models


class BusinessUnitFactory(BaseFactory):
    class Meta:
        model = models.BusinessUnit

    name = factory.Sequence("Business unit #{}".format)
    siret = factory.Sequence("{:014}".format)

    bankAccount = factory.SubFactory("pcapi.core.offers.factories.BankInformationFactory")


class PricingFactory(BaseFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    businessUnit = factory.SelfAttribute("booking.venue.businessUnit")
    valueDate = factory.SelfAttribute("booking.dateUsed")
    amount = LazyAttribute(lambda pricing: int(100 * pricing.booking.total_amount))
    standardRule = "full reimbursement"
    revenue = LazyAttribute(lambda pricing: int(100 * pricing.booking.total_amount))
