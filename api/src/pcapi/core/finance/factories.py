import datetime
import decimal
import secrets
import typing

import factory
import schwifty

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.factories import BaseFactory
from pcapi.core.finance import reimbursement_rules
from pcapi.utils import date as date_utils

from . import api
from . import conf
from . import models


class RecreditFactory(BaseFactory):
    class Meta:
        model = models.Recredit

    deposit = factory.SubFactory(users_factories.DepositGrantFactory)
    amount = factory.LazyAttribute(
        lambda recredit: conf.BONUS_CREDIT_AMOUNT
        if recredit.recreditType == models.RecreditType.BONUS_CREDIT
        else conf.RECREDIT_TYPE_AMOUNT_MAPPING[recredit.recreditType]
    )
    recreditType = models.RecreditType.RECREDIT_16


class BankAccountFactory(BaseFactory):
    class Meta:
        model = models.BankAccount

    offerer = factory.SubFactory(offerers_factories.OffererFactory)
    label = factory.Sequence(lambda n: f"Libellé des coordonnées bancaires n°{n}")
    iban = factory.LazyAttributeSequence(
        lambda o, n: schwifty.IBAN.generate("FR", bank_code="10010", account_code=f"{n:010}").compact
    )
    status = models.BankAccountApplicationStatus.ACCEPTED
    dsApplicationId = factory.Sequence(lambda n: 1000000 + n + 1)


class CaledonianBankAccountFactory(BankAccountFactory):
    offerer = factory.SubFactory(offerers_factories.CaledonianOffererFactory)
    label = factory.Sequence(lambda n: f"Coordonnées bancaires calédoniennes n°{n}")
    iban = factory.LazyAttributeSequence(
        lambda o, n: schwifty.IBAN.generate("NC", bank_code="14889", account_code=f"988{n:07}").compact
    )


class BankAccountStatusHistoryFactory(BaseFactory):
    class Meta:
        model = models.BankAccountStatusHistory

    bankAccount = factory.SubFactory(BankAccountFactory)


class _BaseFinanceEventFactory(BaseFactory):
    class Meta:
        model = models.FinanceEvent

    pricingPointId: int | None = None  # see `_create()` below

    @classmethod
    def _create(
        cls,
        model_class: type[models.FinanceEvent],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.FinanceEvent:
        if kwargs.get("collectiveBooking"):
            kwargs["booking"] = None  # override default Booking
        booking = kwargs.get("booking") or kwargs.get("collectiveBooking")
        assert booking  # make mypy happy
        if not kwargs["pricingPointId"]:
            venue = booking.venue
            kwargs["pricingPointId"] = venue.current_pricing_point_id
        if "status" not in kwargs:
            kwargs["status"] = (
                models.FinanceEventStatus.READY if kwargs["pricingPointId"] else models.FinanceEventStatus.PENDING
            )
        if kwargs["pricingPointId"]:
            kwargs.setdefault(
                "pricingOrderingDate",
                api.get_pricing_ordering_date(booking),
            )
        return super()._create(model_class, *args, **kwargs)


class UsedBookingFinanceEventFactory(_BaseFinanceEventFactory):
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    motive = models.FinanceEventMotive.BOOKING_USED
    venue = factory.LazyAttribute(lambda event: event.booking.venue)
    valueDate = factory.LazyAttribute(lambda event: event.booking.dateUsed)


class UsedCollectiveBookingFinanceEventFactory(_BaseFinanceEventFactory):
    collectiveBooking = factory.SubFactory(educational_factories.UsedCollectiveBookingFactory)
    motive = models.FinanceEventMotive.BOOKING_USED
    venue = factory.LazyAttribute(lambda event: event.collectiveBooking.venue)
    valueDate = factory.LazyAttribute(lambda event: event.collectiveBooking.dateUsed)


class FinanceEventFactory(BaseFactory):
    class Meta:
        model = models.FinanceEvent

    valueDate = factory.LazyAttribute(lambda o: (o.booking or o.collectiveBooking).dateUsed)
    pricingOrderingDate = factory.LazyFunction(date_utils.get_naive_utc_now)
    status = models.FinanceEventStatus.PRICED
    motive = models.FinanceEventMotive.BOOKING_USED
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    venue = factory.LazyAttribute(lambda o: o.venue)
    pricingPoint = factory.LazyAttribute(lambda o: o.venue.current_pricing_point)


class _BasePricingFactory(BaseFactory):
    class Meta:
        model = models.Pricing

    event: FinanceEventFactory | None = None  # see `_create()` below
    pricingPoint: offerers_factories.VenueFactory | None = None  # see `_create()` below

    @classmethod
    def _create(
        cls,
        model_class: type[models.Pricing],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Pricing:
        if not kwargs["pricingPoint"]:
            event = kwargs.get("event")
            event_booking = (
                event.booking
                or event.collectiveBooking
                or event.bookingFinanceIncident.booking
                or event.bookingFinanceIncident.collectiveBooking
                if event
                else None
            )
            booking = kwargs.get("booking") or kwargs.get("collectiveBooking") or event_booking
            assert booking  # make mypy happy
            venue = booking.venue
            pricing_point = venue.current_pricing_point
            if not pricing_point:
                offerers_factories.VenuePricingPointLinkFactory(
                    venue=venue,
                    pricingPoint=venue,
                )
                pricing_point = venue
            kwargs["pricingPoint"] = pricing_point
        if not kwargs["event"]:
            booking = kwargs.get("booking")
            if booking:
                event = UsedBookingFinanceEventFactory(
                    booking=booking,
                    status=models.FinanceEventStatus.PRICED,
                )
            else:
                collective_booking = kwargs.get("collectiveBooking")
                assert collective_booking
                event = UsedCollectiveBookingFinanceEventFactory(
                    collectiveBooking=collective_booking,
                    status=models.FinanceEventStatus.PRICED,
                )
            kwargs["event"] = event
        return super()._create(model_class, *args, **kwargs)


class PricingFactory(_BasePricingFactory):
    status = models.PricingStatus.VALIDATED
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    venue = factory.SelfAttribute("booking.venue")
    valueDate = factory.SelfAttribute("booking.dateUsed")
    amount = factory.LazyAttribute(
        lambda pricing: -int(
            100 * (pricing.booking.total_amount if pricing.booking else pricing.event.booking.total_amount)
        )
    )
    standardRule = "Remboursement total pour les offres physiques"
    revenue = factory.LazyAttribute(
        lambda pricing: int(
            100 * (pricing.booking.total_amount if pricing.booking else pricing.event.booking.total_amount)
        )
    )


class CollectivePricingFactory(_BasePricingFactory):
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
    amount = factory.LazyAttribute(lambda line: line.pricing.amount)
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
            date_utils.get_naive_utc_now() - datetime.timedelta(days=365),
            date_utils.get_naive_utc_now() + datetime.timedelta(days=365),
        ]
    )
    amount = 500

    @classmethod
    def _create(
        cls,
        model_class: type[models.CustomReimbursementRule],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.CustomReimbursementRule:
        if kwargs.get("rate") is not None:
            kwargs["amount"] = None
        if kwargs.get("offerer"):
            kwargs["offer"] = None
            kwargs["venue"] = None
        elif kwargs.get("venue"):
            kwargs["offer"] = None  # offerer is already None here
        return super()._create(model_class, *args, **kwargs)


class InvoiceFactory(BaseFactory):
    class Meta:
        model = models.Invoice

    amount = 1000
    reference = factory.Sequence("{:09}".format)
    token = factory.LazyFunction(secrets.token_urlsafe)
    status = models.InvoiceStatus.PAID


class CashflowBatchFactory(BaseFactory):
    class Meta:
        model = models.CashflowBatch

    cutoff = factory.LazyFunction(date_utils.get_naive_utc_now)
    label = factory.Sequence("VIR{}".format)


class CashflowFactory(BaseFactory):
    class Meta:
        model = models.Cashflow

    amount = -1000
    batch = factory.SubFactory(CashflowBatchFactory)
    status = models.CashflowStatus.ACCEPTED
    bankAccount = factory.SubFactory(BankAccountFactory)


class SettlementBatchFactory(BaseFactory[models.SettlementBatch]):
    class Meta:
        model = models.SettlementBatch

    name = factory.Sequence("VIR{}".format)
    label = factory.Sequence("Libellé VIR{}".format)


class SettlementFactory(BaseFactory[models.Settlement]):
    class Meta:
        model = models.Settlement

    settlementDate = factory.LazyFunction(date_utils.get_naive_utc_now)
    externalSettlementId = "0101234"
    bankAccount = factory.SubFactory(BankAccountFactory)
    amount = 10000
    batch = factory.SubFactory(SettlementBatchFactory)


# Factories below are deprecated and should probably NOT BE USED in
# any new test. See comment in `models.py` above the definition of the
# `Payment` model.
REIMBURSEMENT_RULE_DESCRIPTIONS = {t.description for t in reimbursement_rules.REGULAR_RULES}


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    collectiveBooking: educational_factories.CollectiveBookingFactory | None = None
    amount = factory.LazyAttribute(
        lambda payment: payment.booking.total_amount * decimal.Decimal(payment.reimbursementRate)
    )
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule: str | factory.Iterator | None = factory.Iterator(REIMBURSEMENT_RULE_DESCRIPTIONS)
    reimbursementRate: decimal.Decimal | factory.LazyAttribute | None = factory.LazyAttribute(
        lambda payment: reimbursement_rules.get_reimbursement_rule(  # type: ignore[attr-defined]
            payment.collectiveBooking or payment.booking, reimbursement_rules.CustomRuleFinder(), 0
        ).rate
    )
    recipientName = "Récipiendaire"
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    transactionLabel: str | None = None

    @factory.post_generation
    def statuses(
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

    @classmethod
    def _create(
        cls,
        model_class: type[models.Payment],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Payment:
        if kwargs.get("collectiveBooking"):
            kwargs["booking"] = None  # override default Booking
        return super()._create(model_class, *args, **kwargs)


class PaymentStatusFactory(BaseFactory):
    class Meta:
        model = models.PaymentStatus

    payment = factory.SubFactory(PaymentFactory, statuses=[])


class PaymentWithCustomRuleFactory(PaymentFactory):
    amount = factory.LazyAttribute(lambda payment: payment.customReimbursementRule.amount)
    customReimbursementRule = factory.SubFactory(CustomReimbursementRuleFactory)
    reimbursementRule = None
    reimbursementRate = None


class FinanceIncidentFactory(BaseFactory):
    class Meta:
        model = models.FinanceIncident

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    kind = models.IncidentType.OVERPAYMENT
    status = models.IncidentStatus.CREATED
    details = {
        "createdAt": date_utils.get_naive_utc_now().isoformat(),
        "author": "Sandy Box",
        "validator": "",
        "validatedAt": "",
    }
    origin = models.FinanceIncidentRequestOrigin.SUPPORT_JEUNE


class FinanceCommercialGestureFactory(BaseFactory):
    class Meta:
        model = models.FinanceIncident

    venue = factory.SubFactory(offerers_factories.VenueFactory)
    kind = models.IncidentType.COMMERCIAL_GESTURE
    status = models.IncidentStatus.CREATED
    details = {
        "createdAt": date_utils.get_naive_utc_now().isoformat(),
        "authorId": 1,
        "validator": "",
        "validatedAt": "",
    }
    origin = models.FinanceIncidentRequestOrigin.SUPPORT_PRO


class IndividualBookingFinanceCommercialGestureFactory(BaseFactory):
    class Meta:
        model = models.BookingFinanceIncident

    booking = factory.SubFactory(bookings_factories.CancelledBookingFactory)
    incident = factory.SubFactory(FinanceCommercialGestureFactory)
    beneficiary = factory.SelfAttribute("booking.user")
    newTotalAmount = factory.LazyAttribute(lambda x: x.booking.total_amount - 100)


class IndividualBookingFinanceIncidentFactory(BaseFactory):
    class Meta:
        model = models.BookingFinanceIncident

    booking = factory.SubFactory(bookings_factories.ReimbursedBookingFactory)
    incident = factory.SubFactory(FinanceIncidentFactory)
    beneficiary = factory.SelfAttribute("booking.user")
    newTotalAmount = factory.LazyAttribute(lambda x: x.booking.amount * x.booking.quantity - 100)


class CollectiveBookingFinanceIncidentFactory(BaseFactory):
    class Meta:
        model = models.BookingFinanceIncident

    collectiveBooking = factory.SubFactory(educational_factories.ReimbursedCollectiveBookingFactory)
    incident = factory.SubFactory(FinanceIncidentFactory)
    newTotalAmount = 0
