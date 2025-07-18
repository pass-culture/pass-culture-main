import datetime
import decimal
import logging
import uuid

import PIL

import pcapi.connectors.ems as ems_connector
import pcapi.utils.date as utils_date
from pcapi.connectors import thumb_storage
from pcapi.connectors.serialization import ems_serializers
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.finance import api as finance_api
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offers_api
from pcapi.core.offers import exceptions as offers_exceptions
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.local_providers.movie_festivals import api as movie_festivals_api
from pcapi.local_providers.movie_festivals import constants as movie_festivals_constants
from pcapi.models import db
from pcapi.validation.models import entity_validator


logger = logging.getLogger(__name__)

ACCEPTED_FEATURES_MAPPING = {
    "vf": ShowtimeFeatures.VF.value,
    "vo": ShowtimeFeatures.VO.value,
    "video_3d": ShowtimeFeatures.THREE_D.value,
}


class EMSStocks:
    def __init__(
        self,
        connector: ems_connector.EMSScheduleConnector,
        venue_provider: providers_models.VenueProvider,
        site: ems_serializers.SiteWithEvents,
    ):
        self.connector = connector
        self.site = site
        self.created_objects = 0
        self.updated_objects = 0
        self.errored_objects = 0
        self.venue_provider = venue_provider
        self.venue = venue_provider.venue
        self.is_duo = bool(venue_provider.isDuoOffers)
        self.provider = venue_provider.provider
        self.poster_urls_map: dict[str, str | None] = {}
        self.created_offers: set[offers_models.Offer] = set()
        self.price_category_labels: list[offers_models.PriceCategoryLabel] = (
            db.session.query(offers_models.PriceCategoryLabel)
            .filter(offers_models.PriceCategoryLabel.venue == self.venue)
            .all()
        )

    def synchronize(self) -> None:
        for event in self.site.events:
            self.poster_urls_map.update({event.id: event.bill_url})

            product = self.get_or_create_movie_product(event)
            offer = self.get_or_create_offer(event, self.provider.id, self.venue)
            offer = self.fill_offer_attributes(offer, product, event)
            errors = entity_validator.validate(offer)
            if errors and len(errors.errors) > 0:
                self.created_objects -= 1
                self.errored_objects += 1
                continue
            db.session.add(offer)

            for session in event.sessions:
                stock = self.get_or_create_stock(session, event, offer)
                stock.offer = offer
                stock = self.fill_stock_attributes(stock, session)
                errors = entity_validator.validate(stock)
                if errors and len(errors.errors) > 0:
                    self.created_objects -= 1
                    self.errored_objects += 1
                    continue
                db.session.add(stock)

            self.created_offers.add(offer)

        self.venue_provider.lastSyncDate = datetime.datetime.utcnow()
        db.session.add(self.venue_provider)

        db.session.commit()

        for offer in self.created_offers:
            assert offer.idAtProvider  # helps mypy
            movie_id = _get_movie_id_from_id_at_provider(offer.idAtProvider)
            poster_url = self.poster_urls_map.get(movie_id)
            if not poster_url:
                continue
            poster_url = poster_url.replace("/120/", "/600/")
            try:
                thumb = self.connector.get_movie_poster_from_api(poster_url)
            except ems_connector.EMSAPIException:
                logger.info(
                    "Could not fetch movie poster",
                    extra={
                        "provider": "ems",
                        "url": poster_url,
                    },
                )
                thumb = None
            if not thumb:
                continue

            if offer.product and not offer.product.productMediations:
                try:
                    image_id = str(uuid.uuid4())
                    mediation = offers_models.ProductMediation(
                        productId=offer.product.id,
                        lastProvider=self.provider,
                        imageType=offers_models.ImageType.POSTER,
                        uuid=image_id,
                    )
                    db.session.add(mediation)
                    thumb_storage.create_thumb(
                        offer.product,
                        thumb,
                        storage_id_suffix_str="",
                        keep_ratio=True,
                        object_id=image_id,
                    )
                    db.session.commit()
                except (offers_exceptions.ImageValidationError, PIL.UnidentifiedImageError) as e:
                    logger.warning("Error: Offer image could not be created. Reason: %s", e)

        offer_ids = {offer.id for offer in self.created_offers}
        search.async_index_offer_ids(
            offer_ids,
            reason=search.IndexationReason.STOCK_SYNCHRONIZATION,
            log_extra={"provider": "ems"},
        )

        logger.info(
            "Synchronization of objects of venue=%s, created=%d, updated=%d, errors=%s",
            self.venue.id,
            self.created_objects,
            self.updated_objects,
            self.errored_objects,
        )

    def get_or_create_movie_product(self, movie: ems_serializers.Event) -> offers_models.Product | None:
        generic_movie = movie.to_generic_movie()
        id_at_providers = _build_movie_uuid_for_offer(movie.id, self.venue)
        product = offers_api.upsert_movie_product_from_provider(generic_movie, self.provider, id_at_providers)

        return product

    def get_or_create_offer(
        self, event: ems_serializers.Event, provider_id: int, venue: offerers_models.Venue
    ) -> offers_models.Offer:
        movie_offer_uuid = _build_movie_uuid_for_offer(event.id, venue.id)
        offer = db.session.query(offers_models.Offer).filter_by(idAtProvider=movie_offer_uuid).one_or_none()
        if offer:
            return offer
        offer = offers_models.Offer()
        offer.idAtProvider = movie_offer_uuid
        offer.lastProviderId = provider_id
        offer.subcategoryId = subcategories.SEANCE_CINE.id

        offer.venueId = venue.id
        offer.offererAddress = self.venue.offererAddress
        offer.bookingEmail = venue.bookingEmail
        offer.withdrawalDetails = venue.withdrawalDetails
        offer.publicationDatetime = offer.publicationDatetime or utils_date.get_naive_utc_now()
        self.created_objects += 1
        return offer

    def fill_offer_attributes(
        self, offer: offers_models.Offer, product: offers_models.Product | None, event: ems_serializers.Event
    ) -> offers_models.Offer:
        offer.isDuo = self.is_duo
        if product:
            offer.name = product.name
            offer.product = product
        else:
            if event.title:
                offer.name = event.title
            if event.synopsis:
                offer.description = event.synopsis
            if event.duration:
                offer.durationMinutes = event.duration
        return offer

    def get_or_create_stock(
        self, session: ems_serializers.Session, event: ems_serializers.Event, offer: offers_models.Offer
    ) -> offers_models.Stock:
        session_stock_uuid = _build_session_uuid_for_stock(event.id, offer.venueId, session.id)
        stock = db.session.query(offers_models.Stock).filter_by(idAtProviders=session_stock_uuid).one_or_none()
        if stock:
            return stock
        stock = offers_models.Stock()
        stock.idAtProviders = session_stock_uuid
        self.created_objects += 1
        return stock

    def fill_stock_attributes(
        self, stock: offers_models.Stock, session: ems_serializers.Session
    ) -> offers_models.Stock:
        stock.quantity = None

        # sort features list to have always same order for all providers VO/VF then 3D
        stock.features = sorted(
            [
                ACCEPTED_FEATURES_MAPPING.get(feature)
                for feature in session.features
                if feature in ACCEPTED_FEATURES_MAPPING
            ],
            reverse=True,
        )

        local_tz = utils_date.get_department_timezone(self.venue.departementCode)
        beginning_datetime = datetime.datetime.strptime(session.date, "%Y%m%d%H%M")
        beginning_datetime_no_tz = utils_date.local_datetime_to_default_timezone(beginning_datetime, local_tz).replace(
            tzinfo=None
        )
        old_beginning_datetime = stock.beginningDatetime
        stock.beginningDatetime = beginning_datetime_no_tz
        stock.bookingLimitDatetime = beginning_datetime_no_tz
        _maybe_update_finance_event_pricing_date(stock, old_beginning_datetime)

        if movie_festivals_api.should_apply_movie_festival_rate(stock.offer.id, stock.beginningDatetime.date()):
            stock.price = movie_festivals_constants.FESTIVAL_RATE
            stock.priceCategory = self.get_or_create_price_category(
                stock,
                movie_festivals_constants.FESTIVAL_RATE,
                movie_festivals_constants.FESTIVAL_NAME,
            )
        else:
            show_price = decimal.Decimal(session.pass_culture_price)
            price_label = f"Tarif pass Culture {show_price}€"
            price_category = self.get_or_create_price_category(stock, show_price, price_label)
            stock.price = show_price
            stock.priceCategory = price_category

        return stock

    def get_or_create_price_category(
        self, stock: offers_models.Stock, price: decimal.Decimal, price_label: str
    ) -> offers_models.PriceCategory:
        with db.session.no_autoflush:
            offer_price_categories = stock.offer.priceCategories
            for offer_price_category in offer_price_categories:
                if offer_price_category.price == price and offer_price_category.label == price_label:
                    return offer_price_category

            price_category_label = self.get_or_create_price_category_label(price_label)
            price_category = offers_models.PriceCategory(
                price=price, priceCategoryLabel=price_category_label, offer=stock.offer
            )

            return price_category

    def get_or_create_price_category_label(self, price_label: str) -> offers_models.PriceCategoryLabel:
        price_category_label = next((label for label in self.price_category_labels if label.label == price_label), None)
        if not price_category_label:
            price_category_label = offers_models.PriceCategoryLabel(label=price_label, venue=self.venue)
            self.price_category_labels.append(price_category_label)

        return price_category_label


def _build_session_uuid_for_stock(movie_id: str, venue_id: int, session_id: str) -> str:
    return f"{_build_movie_uuid_for_offer(movie_id, venue_id)}#{session_id}"


def _build_movie_uuid_for_offer(movie_id: str, venue_id: int) -> str:
    return f"{movie_id}%{venue_id}%EMS"


def _get_movie_id_from_id_at_provider(id_at_provider: str) -> str:
    return id_at_provider.split("%")[0]


def _maybe_update_finance_event_pricing_date(
    stock: offers_models.Stock,
    old_beginning_datetime: datetime.datetime | None,
) -> None:
    assert stock.beginningDatetime is not None  # to make mypy happy
    if (
        stock.id is not None
        and old_beginning_datetime is not None
        and stock.beginningDatetime.replace(tzinfo=None) != old_beginning_datetime
    ):
        finance_api.update_finance_event_pricing_date(stock)
