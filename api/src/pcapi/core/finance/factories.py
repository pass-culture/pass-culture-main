import datetime
import decimal
import secrets

import factory
import schwifty

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import BaseFactory
from pcapi.domain import reimbursement

from . import models


class BankInformationFactory(BaseFactory):
    class Meta:
        model = models.BankInformation

    bic = "BDFEFRPP"
    iban = factory.LazyAttributeSequence(
        lambda o, n: schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{n:010}").compact
    )
    status = models.BankInformationStatus.ACCEPTED


class BusinessUnitFactory(BaseFactory):
    class Meta:
        model = models.BusinessUnit

    name = factory.Sequence("Business unit #{}".format)
    siret = factory.Sequence("{:014}".format)
    status = models.BusinessUnitStatus.ACTIVE

    bankAccount = factory.SubFactory(BankInformationFactory)


class BusinessUnitVenueLinkFactory(BaseFactory):
    class Meta:
        model = models.BusinessUnitVenueLink

    businessUnit = factory.SelfAttribute("venue.businessUnit")
    venue = factory.SubFactory(offerers_factories.VenueFactory)
    timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            None,
        ]
    )


class PricingFactory(BaseFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    booking = factory.SubFactory(bookings_factories.UsedIndividualBookingFactory)
    venue = factory.SelfAttribute("booking.venue")
    businessUnit = factory.SelfAttribute("booking.venue.businessUnit")
    siret = factory.LazyAttribute(
        lambda pricing: pricing.booking.venue.siret or pricing.booking.venue.businessUnit.siret
    )
    pricingPointId = factory.SelfAttribute("booking.venue.current_pricing_point_id")
    valueDate = factory.SelfAttribute("booking.dateUsed")
    amount = factory.LazyAttribute(lambda pricing: -int(100 * pricing.booking.total_amount))
    standardRule = "Remboursement total pour les offres physiques"
    revenue = factory.LazyAttribute(lambda pricing: int(100 * pricing.booking.total_amount))


class CollectivePricingFactory(BaseFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    collectiveBooking = factory.SubFactory(UsedCollectiveBookingFactory)
    venue = factory.SelfAttribute("collectiveBooking.venue")
    businessUnit = factory.SelfAttribute("collectiveBooking.venue.businessUnit")
    siret = factory.SelfAttribute("collectiveBooking.venue.siret")
    valueDate = factory.SelfAttribute("collectiveBooking.dateUsed")
    amount = factory.LazyAttribute(lambda pricing: -int(100 * pricing.collectiveBooking.collectiveStock.price))
    standardRule = "Remboursement total pour les offres éducationnelles"
    revenue = factory.LazyAttribute(lambda pricing: int(100 * pricing.collectiveBooking.collectiveStock.price))


class PricingLineFactory(BaseFactory):
    class Meta:
        model = models.PricingLine

    pricing = factory.SubFactory(PricingFactory)
    amount = factory.LazyAttribute(lambda line: -line.pricing.amount)
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
    reimbursementPoint = factory.SubFactory(offerers_factories.VenueFactory)
    amount = 1000
    reference = factory.Sequence("{:09}".format)
    token = factory.LazyFunction(secrets.token_urlsafe)


class CashflowBatchFactory(BaseFactory):
    class Meta:
        model = models.CashflowBatch

    cutoff = factory.LazyFunction(datetime.datetime.utcnow)
    label = factory.Sequence("VIR{}".format)


class CashflowFactory(BaseFactory):
    class Meta:
        model = models.Cashflow

    amount = -1000
    batch = factory.SubFactory(CashflowBatchFactory)
    status = models.CashflowStatus.ACCEPTED
    # FIXME (dbaty, 2022-07-08): must be adapted for reimbursement points
    bankAccount = factory.SelfAttribute("businessUnit.bankAccount")


# Factories below are deprecated and should probably NOT BE USED in
# any new test. See comment in `models.py` above the definition of the
# `Payment` model.
REIMBURSEMENT_RULE_DESCRIPTIONS = {t.description for t in reimbursement.REGULAR_RULES}


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.UsedIndividualBookingFactory)
    amount = factory.LazyAttribute(
        lambda payment: payment.booking.total_amount * decimal.Decimal(payment.reimbursementRate)
    )
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule = factory.Iterator(REIMBURSEMENT_RULE_DESCRIPTIONS)
    reimbursementRate = factory.LazyAttribute(
        lambda payment: reimbursement.get_reimbursement_rule(  # type: ignore [attr-defined]
            payment.booking, reimbursement.CustomRuleFinder(), decimal.Decimal(0)
        ).rate
    )
    recipientName = "Récipiendaire"
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    transactionLabel = None

    @factory.post_generation
    def statuses(obj, create, extracted, **kwargs):  # type: ignore [no-untyped-def] # pylint: disable=no-self-argument

        if not create:
            return None
        if extracted is not None:
            return extracted
        status = PaymentStatusFactory(payment=obj, status=models.TransactionStatus.PENDING)
        return [status]


class PaymentStatusFactory(BaseFactory):
    class Meta:
        model = models.PaymentStatus

    payment = factory.SubFactory(PaymentFactory, statuses=[])


class PaymentWithCustomRuleFactory(PaymentFactory):
    amount = factory.LazyAttribute(lambda payment: payment.customReimbursementRule.amount)
    customReimbursementRule = factory.SubFactory(payments_factories.CustomReimbursementRuleFactory)
    reimbursementRule = None
    reimbursementRate = None
