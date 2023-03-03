import datetime
import typing

import factory

import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
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
    user = factory.SubFactory(users_factories.BeneficiaryGrant18Factory)
    deposit = factory.LazyAttribute(lambda o: o.user.deposit)
    amount = factory.SelfAttribute("stock.price")
    status = models.BookingStatus.CONFIRMED
    priceCategoryLabel = factory.Maybe(
        "stock.priceCategory", factory.SelfAttribute("stock.priceCategory.priceCategoryLabel.label"), None
    )

    @factory.post_generation
    def cancellation_limit_date(
        self,
        create: bool,
        extracted: datetime.datetime | None,
        **kwargs: typing.Any,
    ) -> None:
        if extracted:
            self.cancellationLimitDate = extracted
        else:
            self.cancellationLimitDate = api.compute_cancellation_limit_date(
                self.stock.beginningDatetime, self.dateCreated
            )  # type: ignore [assignment]
        db.session.add(self)
        db.session.commit()

    @factory.post_generation
    def cancellation_date(
        self,
        create: bool,
        extracted: datetime.datetime | None,
        **kwargs: typing.Any,
    ) -> None:
        # the public.save_cancellation_date() psql trigger overrides the extracted cancellationDate
        if extracted:
            self.cancellationDate = extracted
            db.session.add(self)
            db.session.flush()

    @classmethod
    def _create(
        cls,
        model_class: typing.Type[models.Booking],
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> models.Booking:
        if not kwargs.get("status") == models.BookingStatus.CANCELLED:
            stock: offers_models.Stock = kwargs["stock"]
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


class ReimbursedBookingFactory(BookingFactory):
    status = models.BookingStatus.REIMBURSED
    dateUsed = factory.LazyFunction(datetime.datetime.utcnow)
    reimbursementDate = factory.LazyFunction(datetime.datetime.utcnow)
