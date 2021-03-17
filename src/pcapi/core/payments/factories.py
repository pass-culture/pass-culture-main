import factory

from pcapi import models
import pcapi.core.bookings.conf as bookings_conf
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.domain import reimbursement
from pcapi.models import payment_status
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries

from . import api


ALL_REIMBURSEMENT_RULES = {t.name for t in list(reimbursement.ReimbursementRules)}


class DepositFactory(BaseFactory):
    class Meta:
        model = models.Deposit

    user = factory.SubFactory(users_factories.UserFactory)
    source = "public"
    version = 1
    expirationDate = factory.LazyFunction(api._get_expiration_date)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if "amount" in kwargs:
            raise ValueError("You cannot directly set deposit amount: set version instead")
        version = kwargs.get("version")
        if not version:
            version = 2 if feature_queries.is_active(FeatureToggle.APPLY_BOOKING_LIMITS_V2) else 1
        amount = bookings_conf.LIMIT_CONFIGURATIONS[version].TOTAL_CAP
        kwargs["version"] = version
        kwargs["amount"] = amount
        return super()._create(model_class, *args, **kwargs)


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.BookingFactory)
    amount = factory.SelfAttribute("booking.total_amount")
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule = factory.Iterator(ALL_REIMBURSEMENT_RULES)
    reimbursementRate = 30
    recipientName = "Récipiendaire"
    iban = "CF13QSDFGH456789"
    bic = "QSDFGH8Z555"

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
