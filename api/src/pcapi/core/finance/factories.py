import datetime
import secrets

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
    status = models.BusinessUnitStatus.ACTIVE

    bankAccount = factory.SubFactory("pcapi.core.offers.factories.BankInformationFactory")


class PricingFactory(BaseFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    booking = factory.SubFactory(bookings_factories.UsedIndividualBookingFactory)
    businessUnit = factory.SelfAttribute("booking.venue.businessUnit")
    siret = factory.SelfAttribute("booking.venue.siret")
    valueDate = factory.SelfAttribute("booking.dateUsed")
    amount = LazyAttribute(lambda pricing: -int(100 * pricing.booking.total_amount))
    standardRule = "Remboursement total pour les offres physiques"
    revenue = LazyAttribute(lambda pricing: int(100 * pricing.booking.total_amount))


class PricingLineFactory(BaseFactory):
    class Meta:
        model = models.PricingLine

    pricing = factory.SubFactory(PricingFactory)
    amount = LazyAttribute(lambda line: -line.pricing.amount)
    category = models.PricingLineCategory.OFFERER_REVENUE


class PricingLogFactory(BaseFactory):
    class Meta:
        model = models.PricingLog

    pricing = factory.SubFactory(PricingFactory)
    statusBefore = models.PricingStatus.VALIDATED
    statusAfter = models.PricingStatus.CANCELLED
    reason = models.PricingLogReason.MARK_AS_UNUSED


class InvoiceFactory(BaseFactory):
    class Meta:
        model = models.Invoice

    businessUnit = factory.SubFactory(BusinessUnitFactory)
    amount = 1000
    reference = factory.Sequence("{:09}".format)
    token = factory.LazyFunction(secrets.token_urlsafe)


class CashflowBatchFactory(BaseFactory):
    class Meta:
        model = models.CashflowBatch

    cutoff = factory.LazyFunction(datetime.datetime.utcnow)


class CashflowFactory(BaseFactory):
    class Meta:
        model = models.Cashflow

    batch = factory.SubFactory(CashflowBatchFactory)
    status = models.CashflowStatus.ACCEPTED
    bankAccount = factory.SelfAttribute("businessUnit.bankAccount")


class CashflowPricingFactory(BaseFactory):
    class Meta:
        model = models.CashflowPricing

    cashflow = factory.SubFactory(CashflowFactory)
    pricing = factory.SubFactory(PricingFactory, businessUnit=factory.SelfAttribute("..cashflow.businessUnit"))
