import datetime

import factory

from pcapi.core.educational.factories import EducationalBookingFactory as EducationalBookingSubFactory
from pcapi.core.educational.factories import PendingEducationalBookingFactory as PendingEducationalBookingSubFactory
from pcapi.core.educational.factories import RefusedEducationalBookingFactory as RefusedEducationalBookingSubFactory
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import BaseFactory
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils.token import random_token

from . import api
from . import models


class BookingFactory(BaseFactory):
    class Meta:
        model = models.Booking

    quantity = 1
    stock = factory.SubFactory(offers_factories.StockFactory)
    token = factory.LazyFunction(random_token)
    user = None
    amount = factory.SelfAttribute("stock.price")
    status = models.BookingStatus.CONFIRMED

    @factory.post_generation
    def cancellation_limit_date(self, create, extracted, **kwargs):
        if extracted:
            self.cancellationLimitDate = extracted
        else:
            self.cancellationLimitDate = api.compute_cancellation_limit_date(
                self.stock.beginningDatetime, self.dateCreated
            )
        db.session.add(self)
        db.session.commit()

    @factory.post_generation
    def cancellation_date(self, create, extracted, **kwargs):
        # the public.save_cancellation_date() psql trigger overrides the extracted cancellationDate
        if extracted:
            self.cancellationDate = extracted
            db.session.add(self)
            db.session.flush()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if not kwargs.get("status") == models.BookingStatus.CANCELLED:
            stock = kwargs.get("stock")
            stock.dnBookedQuantity = stock.dnBookedQuantity + kwargs.get("quantity", 1)
            kwargs["stock"] = stock
        kwargs["venue"] = kwargs["stock"].offer.venue
        kwargs["offerer"] = kwargs["stock"].offer.venue.managingOfferer
        return super()._create(model_class, *args, **kwargs)


class UsedBookingFactory(BookingFactory):
    status = models.BookingStatus.USED
    dateUsed = factory.LazyFunction(datetime.datetime.utcnow)


class CancelledBookingFactory(BookingFactory):
    status = models.BookingStatus.CANCELLED
    cancellationDate = factory.LazyFunction(datetime.datetime.utcnow)
    cancellationReason = models.BookingCancellationReasons.BENEFICIARY


class EducationalBookingFactory(BookingFactory):
    educationalBooking = factory.SubFactory(EducationalBookingSubFactory)
    stock = factory.SubFactory(offers_factories.EducationalEventStockFactory)
    userId = None
    user = None


class UsedEducationalBookingFactory(BookingFactory):
    educationalBooking = factory.SubFactory(EducationalBookingSubFactory)
    stock = factory.SubFactory(offers_factories.EducationalEventStockFactory)
    status = models.BookingStatus.USED
    dateUsed = factory.LazyFunction(datetime.datetime.utcnow)
    userId = None
    user = None


class PendingEducationalBookingFactory(BookingFactory):
    educationalBooking = factory.SubFactory(PendingEducationalBookingSubFactory)
    stock = factory.SubFactory(offers_factories.EducationalEventStockFactory)
    status = models.BookingStatus.PENDING
    userId = None
    user = None


class RefusedEducationalBookingFactory(BookingFactory):
    educationalBooking = factory.SubFactory(RefusedEducationalBookingSubFactory)
    stock = factory.SubFactory(offers_factories.EducationalEventStockFactory)
    status = models.BookingStatus.CANCELLED
    cancellationDate = factory.LazyFunction(datetime.datetime.utcnow)
    cancellationReason = models.BookingCancellationReasons.REFUSED_BY_INSTITUTE
    userId = None
    user = None


class IndividualBookingSubFactory(BaseFactory):
    class Meta:
        model = models.IndividualBooking

    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)

    @factory.post_generation
    def attached_deposit(self, create, extracted, **kwargs):
        if extracted == "forced_none":
            self.deposit = None
            return
        if extracted is not None:
            self.deposit = extracted
            return

        self.deposit = self.user.deposit if self.user.has_active_deposit else None


class IndividualBookingFactory(BookingFactory):
    individualBooking = factory.SubFactory(IndividualBookingSubFactory)
    user = None


class CancelledIndividualBookingFactory(CancelledBookingFactory):
    individualBooking = factory.SubFactory(IndividualBookingSubFactory)
    user = None


class UsedIndividualBookingFactory(UsedBookingFactory):
    individualBooking = factory.SubFactory(IndividualBookingSubFactory)
    user = None
