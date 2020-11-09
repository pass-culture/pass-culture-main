import datetime
from typing import Optional

from flask import current_app as app

from pcapi.connectors import redis
from pcapi.core.offers.repository import get_paginated_offers_for_offerer_venue_and_keywords
from pcapi.domain.admin_emails import send_offer_creation_notification_to_administration
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
from pcapi.repository import user_offerer_queries
from pcapi.routes.serialization.offers_serialize import PostOfferBodyModel
from pcapi.utils.config import PRO_URL
from pcapi.utils.mailing import send_raw_email
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
    if not user_is_admin:
        if venue_id:
            venue = VenueSQLEntity.query.filter_by(id=venue_id).first_or_404()
            offerer_id = offerer_id or venue.managingOffererId
        if offerer_id is not None:
            user_offerer = (
                user_offerer_queries.find_one_or_none_by_user_id_and_offerer_id(
                    user_id=user_id, offerer_id=offerer_id
                )
            )
            validation.check_user_has_rights_on_offerer(user_offerer)

    return get_paginated_offers_for_offerer_venue_and_keywords(
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

    ensure_current_user_has_rights(
        rights=RightsType.editor, offerer_id=venue.managingOffererId, user=user
    )

    if offer_data.product_id:
        offer = initialize_offer_from_product_id(offer_data.product_id)
    else:
        offer = fill_offer_with_new_data(offer_data.dict(by_alias=True), user)
        offer.product.owningOfferer = venue.managingOfferer

    offer.venue = venue
    offer.bookingEmail = offer_data.booking_email
    repository.save(offer)
    send_offer_creation_notification_to_administration(
        offer, user, PRO_URL, send_raw_email
    )

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
