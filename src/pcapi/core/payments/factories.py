import datetime
from decimal import Decimal
import hashlib

import factory

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
from pcapi.domain import reimbursement
from pcapi.models import payment_status

from . import models as payments_models


REIMBURSEMENT_RULE_DESCRIPTIONS = {t.description for t in reimbursement.REGULAR_RULES}


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.UsedBookingFactory)
    amount = factory.LazyAttribute(lambda payment: payment.booking.total_amount * Decimal(payment.reimbursementRate))
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule = factory.Iterator(REIMBURSEMENT_RULE_DESCRIPTIONS)
    reimbursementRate = factory.LazyAttribute(
        lambda payment: reimbursement.get_reimbursement_rule(
            payment.booking, reimbursement.CustomRuleFinder(), Decimal(0)
        ).rate
    )
    recipientName = "Récipiendaire"
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"
    transactionLabel = None

    @factory.post_generation
    def statuses(obj, create, extracted, **kwargs):  # pylint: disable=no-self-argument

        if not create:
            return None
        if extracted is not None:
            return extracted
        status = PaymentStatusFactory(payment=obj, status=payment_status.TransactionStatus.PENDING)
        return [status]


class PaymentStatusFactory(BaseFactory):
    class Meta:
        model = models.PaymentStatus

    payment = factory.SubFactory(PaymentFactory, statuses=[])


class PaymentMessageFactory(BaseFactory):
    class Meta:
        model = models.PaymentMessage

    name = factory.Sequence("payment message {0}".format)
    checksum = factory.LazyFunction(lambda: hashlib.sha1(datetime.datetime.now().isoformat().encode("utf-8")).digest())


class CustomReimbursementRuleFactory(BaseFactory):
    class Meta:
        model = payments_models.CustomReimbursementRule

    offer = factory.SubFactory(offers_factories.OfferFactory)
    timespan = factory.LazyFunction(
        lambda: [
            datetime.datetime.now() - datetime.timedelta(days=365),
            datetime.datetime.now() + datetime.timedelta(days=365),
        ]
    )
    amount = 5

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "rate" in kwargs:
            kwargs["amount"] = None
        if "offerer" in kwargs:
            kwargs["offer"] = None
        return super()._create(model_class, *args, **kwargs)


class PaymentWithCustomRuleFactory(PaymentFactory):
    amount = factory.LazyAttribute(lambda payment: payment.customReimbursementRule.amount)
    customReimbursementRule = factory.SubFactory(CustomReimbursementRuleFactory)
    reimbursementRule = None
    reimbursementRate = None
