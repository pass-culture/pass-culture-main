import datetime
from typing import Optional

from flask import current_app as app

from pcapi.connectors import redis
import pcapi.core.bookings.repository as bookings_repository
import pcapi.core.offers.repository as offers_repository
from pcapi.domain import admin_emails
from pcapi.domain import user_emails
import pcapi.domain.allocine as domain_allocine
from pcapi.domain.create_offer import fill_offer_with_new_data
from pcapi.domain.create_offer import initialize_offer_from_product_id
from pcapi.domain.pro_offers.paginated_offers_recap import PaginatedOffersRecap
from pcapi.models import RightsType
from pcapi.models import StockSQLEntity
from pcapi.models import UserSQLEntity
from pcapi.models import VenueSQLEntity
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries
from pcapi.repository import repository
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.utils import mailing
from pcapi.utils.config import PRO_URL
from pcapi.utils.rest import ensure_current_user_has_rights
from pcapi.utils.rest import load_or_raise_error

from . import models
from . import validation


DEFAULT_OFFERS_PER_PAGE = 20
DEFAULT_PAGE = 1


def list_offers_for_pro_user(
    user_id: int,
    user_is_admin: bool,
    type_id: Optional[str],
    offerer_id: Optional[int],
    offers_per_page: Optional[int],
    page: Optional[int],
    venue_id: Optional[int] = None,
    name_keywords: Optional[str] = None,
    status: Optional[str] = None,
    creation_mode: Optional[str] = None,
) -> PaginatedOffersRecap:
    return offers_repository.get_paginated_offers_for_offerer_venue_and_keywords(
        user_id=user_id,
        user_is_admin=user_is_admin,
        offerer_id=offerer_id,
        offers_per_page=offers_per_page or DEFAULT_OFFERS_PER_PAGE,
        venue_id=venue_id,
        type_id=type_id,
        page=page or DEFAULT_PAGE,
        name_keywords=name_keywords,
        status=status,
        creation_mode=creation_mode,
    )


def create_offer(offer_data: PostOfferBodyModel, user: UserSQLEntity) -> models.Offer:
    venue = load_or_raise_error(VenueSQLEntity, offer_data.venue_id)

    ensure_current_user_has_rights(rights=RightsType.editor, offerer_id=venue.managingOffererId, user=user)

    if offer_data.product_id:
        offer = initialize_offer_from_product_id(offer_data.product_id)
    else:
        offer = fill_offer_with_new_data(offer_data.dict(by_alias=True), user)
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = offer_data.booking_email
    repository.save(offer)
    admin_emails.send_offer_creation_notification_to_administration(offer, user, PRO_URL, mailing.send_raw_email)

    return offer


def create_stock(
    offer: models.Offer,
    price: float,
    quantity: int = None,
    beginning: datetime.datetime = None,
    booking_limit_datetime: datetime.datetime = None,
) -> StockSQLEntity:
    """Return the new stock or raise an exception if it's not possible."""
    validation.check_required_dates_for_stock(offer, beginning, booking_limit_datetime)
    validation.check_offer_is_editable(offer)
    validation.check_stocks_are_editable_for_offer(offer)

    # FIXME (dbaty, 2020-11-06): this is not right. PcOject's constructor
    # should allow to call it with `Stock(offer=offer, ...)`
    stock = models.StockSQLEntity()
    stock.offer = offer
    stock.price = price
    stock.quantity = quantity
    stock.beginningDatetime = beginning
    stock.bookingLimitDatetime = booking_limit_datetime

    repository.save(stock)

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=offer.id)

    return stock


def edit_stock(
    stock: StockSQLEntity,
    price: int = None,
    quantity: int = None,
    beginning: datetime.datetime = None,
    booking_limit_datetime: datetime.datetime = None,
) -> StockSQLEntity:
    validation.check_stock_is_updatable(stock)
    validation.check_required_dates_for_stock(stock.offer, beginning, booking_limit_datetime)

    updates = {
        "price": price,
        "quantity": quantity,
        "beginningDatetime": beginning,
        "bookingLimitDatetime": booking_limit_datetime,
    }
    if stock.offer.isFromAllocine:
        # fmt: off
        updated_fields = {
            attr
            for attr, new_value in updates.items()
            if new_value != getattr(stock, attr)
        }
        # fmt: on
        validation.check_update_only_allowed_stock_fields_for_allocine_offer(updated_fields)
        stock.fieldsUpdated = list(updated_fields)

    previous_beginning = stock.beginningDatetime

    for model_attr, value in updates.items():
        setattr(stock, model_attr, value)
    repository.save(stock)

    if beginning != previous_beginning:
        bookings = bookings_repository.find_not_cancelled_bookings_by_stock(stock)
        if bookings:
            try:
                user_emails.send_batch_stock_postponement_emails_to_users(bookings, send_email=mailing.send_raw_email)
            except mailing.MailServiceException as mail_service_exception:
                # fmt: off
                app.logger.exception(
                    "Could not notify beneficiaries about update of stock=%s: exc",
                    stock.id,
                    mail_service_exception,
                )
                # fmt: on

    if feature_queries.is_active(FeatureToggle.SYNCHRONIZE_ALGOLIA):
        redis.add_offer_id(client=app.redis_client, offer_id=stock.offerId)

    return stock
