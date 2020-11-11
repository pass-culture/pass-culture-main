import factory

from pcapi import models
import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.domain import reimbursement


ALL_REIMBURSEMENT_RULES = {t.name for t in list(reimbursement.ReimbursementRules)}


class DepositFactory(BaseFactory):
    class Meta:
        model = models.Deposit

    user = factory.SubFactory(users_factories.UserFactory)
    amount = 500
    source = "public"


class PaymentFactory(BaseFactory):
    class Meta:
        model = models.Payment

    author = "batch"
    booking = factory.SubFactory(bookings_factories.BookingFactory)
    amount = factory.SelfAttribute("booking.total_amount")
    recipientSiren = factory.SelfAttribute("booking.stock.offer.venue.managingOfferer.siren")
    reimbursementRule = factory.Iterator(ALL_REIMBURSEMENT_RULES)
    reimbursementRate = 30
