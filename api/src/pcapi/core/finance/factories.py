import datetime
import decimal
import secrets
import typing

import factory
import schwifty

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.domain import reimbursement

from . import conf
from . import models


class RecreditFactory(BaseFactory):
    class Meta:
        model = models.Recredit

    deposit = factory.SubFactory(users_factories.DepositGrantFactory)
    amount = factory.LazyAttribute(lambda recredit: conf.RECREDIT_TYPE_AMOUNT_MAPPING[recredit.recreditType])
    recreditType = models.RecreditType.RECREDIT_16


class BankInformationFactory(BaseFactory):
    class Meta:
        model = models.BankInformation

    bic = "BDFEFRPP"
    iban = factory.LazyAttributeSequence(
        lambda o, n: schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{n:010}").compact
    )
    status = models.BankInformationStatus.ACCEPTED


class _BasePricingFactory(BaseFactory):
    pricingPointId = None  # see `_create()` below

    @classmethod
    def _create(
        cls,
        model_class: typing.Type[models.Pricing],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Pricing:
        if not kwargs["pricingPointId"]:
            booking = kwargs.get("booking") or kwargs.get("collectiveBooking")
            assert booking  # make mypy happy
            venue = booking.venue
            pricing_point_id = venue.current_pricing_point_id
            if not pricing_point_id:
                offerers_factories.VenuePricingPointLinkFactory(
                    venue=venue,
                    pricingPoint=venue,
                )
                pricing_point_id = venue.id
            kwargs["pricingPointId"] = pricing_point_id
        return super()._create(model_class, *args, **kwargs)


class PricingFactory(_BasePricingFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    venue = factory.SelfAttribute("booking.venue")
    valueDate = factory.SelfAttribute("booking.dateUsed")
    amount = factory.LazyAttribute(lambda pricing: -int(100 * pricing.booking.total_amount))
    standardRule = "Remboursement total pour les offres physiques"
    revenue = factory.LazyAttribute(lambda pricing: int(100 * pricing.booking.total_amount))


class CollectivePricingFactory(_BasePricingFactory):
    class Meta:
        model = models.Pricing

    status = models.PricingStatus.VALIDATED
    collectiveBooking = factory.SubFactory(UsedCollectiveBookingFactory)
    venue = factory.SelfAttribute("collectiveBooking.venue")
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


class CustomReimbursementRuleFactory(BaseFactory):
    class Meta:
        model = models.CustomReimbursementRule

    offer = factory.SubFactory(offers_factories.OfferFactory)
    timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.utcnow() - datetime.timedelta(days=365),
            datetime.datetime.utcnow() + datetime.timedelta(days=365),
        ]
    )
    amount = 5

    @classmethod
    def _create(
        cls,
        model_class: typing.Type[models.CustomReimbursementRule],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.CustomReimbursementRule:
        if "rate" in kwargs:
            kwargs["amount"] = None
        if "offerer" in kwargs:
            kwargs["offer"] = None
        return super()._create(model_class, *args, **kwargs)


class InvoiceFactory(BaseFactory):
    class Meta:
        model = models.Invoice

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
    reimbursementPoint = None
    bankAccount = factory.LazyAttribute(lambda cashflow: cashflow.reimbursementPoint.bankInformation)


# Factories below are deprecated and should probably NOT BE USED in
# any new test. See comment in `models.py` above the definition of the
# `Payment` model.
REIMBURSEMENT_RULE_DESCRIPTIONS = {t.description for t in reimbursement.REGULAR_RULES}


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    amount = factory.LazyAttribute(
        lambda payment: payment.booking.total_amount * decimal.Decimal(payment.reimbursementRate)
    )
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule = factory.Iterator(REIMBURSEMENT_RULE_DESCRIPTIONS)
    reimbursementRate = factory.LazyAttribute(
        lambda payment: reimbursement.get_reimbursement_rule(  # type: ignore [attr-defined]
            payment.booking, reimbursement.CustomRuleFinder(), 0
        ).rate
    )
    recipientName = "Récipiendaire"
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    transactionLabel = None

    @factory.post_generation
    def statuses(  # pylint: disable=no-self-argument
        obj,
        create: bool,
        extracted: list[models.PaymentStatus],
        **kwargs: typing.Any,
    ) -> list[models.PaymentStatus] | None:
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
    customReimbursementRule = factory.SubFactory(CustomReimbursementRuleFactory)
    reimbursementRule = None
    reimbursementRate = None
