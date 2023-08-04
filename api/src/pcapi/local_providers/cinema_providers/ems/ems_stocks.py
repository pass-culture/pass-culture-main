import datetime
import decimal
import logging

from pcapi.connectors import ems
from pcapi.connectors.serialization import ems_serializers
from pcapi.connectors.thumb_storage import create_thumb
from pcapi.core import search
from pcapi.core.categories import subcategories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import models as providers_models
from pcapi.local_providers.cinema_providers.constants import ShowtimeFeatures
from pcapi.models import db
from pcapi.validation.models import entity_validator


logger = logging.getLogger(__name__)

ACCEPTED_FEATURES_MAPPING = {
    "vf": ShowtimeFeatures.VF.value,
    "vo": ShowtimeFeatures.VO.value,
    "video_3d": ShowtimeFeatures.THREE_D.value,
}


class EMSStocks:
    def __init__(self, venue_provider: providers_models.VenueProvider, site: ems_serializers.Site):
        self.site = site
        self.created_objects = 0
        self.updated_objects = 0
        self.errored_objects = 0
        self.venue_provider = venue_provider
        self.venue = venue_provider.venue
        self.provider = venue_provider.provider
        self.poster_urls_map: dict[int, str | None] = {}
        self.created_products: set[offers_models.Product] = set()
        self.created_offers: set[offers_models.Offer] = set()
        self.price_category_labels: list[
            offers_models.PriceCategoryLabel
        ] = offers_models.PriceCategoryLabel.query.filter(offers_models.PriceCategoryLabel.venue == self.venue).all()

    def synchronize(self) -> None:
        for event in self.site.events:
            product = self.get_or_create_product(event, self.provider.id)
            product = self.fill_product_attribut(product, event)
            errors = entity_validator.validate(product)
            if errors and len(errors.errors) > 0:
                self.created_objects -= 1
                self.errored_objects += 1
                continue
            db.session.add(product)

            self.poster_urls_map.update({event.allocine_id: event.bill_url})

            offer = self.get_or_create_offer(event, self.provider.id, self.venue)
            offer.product = product
            offer = self.fill_offer_attribut(offer, event)
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

            self.created_products.add(product)
            self.created_offers.add(offer)

        self.venue_provider.lastSyncDate = datetime.datetime.utcnow()
        db.session.add(self.venue_provider)

        db.session.commit()

        for product in self.created_products:
            assert product.idAtProviders  # helps mypy
            allocine_movie_id = _get_movie_id_from_id_at_provider(product.idAtProviders)
            poster_url = self.poster_urls_map.get(allocine_movie_id)
            if not poster_url:
                continue
            thumb = ems.get_movie_poster_from_api(poster_url.replace("/120/", "/600/"))
            if not thumb:
                continue
            create_thumb(model_with_thumb=product, image_as_bytes=thumb, storage_id_suffix_str="", keep_ratio=True)

        offer_ids = set()
        for offer in self.created_offers:
            offer_ids.add(offer.id)
        search.async_index_offer_ids(offer_ids)

        logger.info(
            "Synchronization of objects of venue=%s, created=%d, updated=%d, errors=%s",
            self.venue.id,
            self.created_objects,
            self.updated_objects,
            self.errored_objects,
        )

    def get_or_create_product(self, event: ems_serializers.Event, provider_id: int) -> offers_models.Product:
        movie_product_uuid = _build_movie_uuid_for_product(event.allocine_id)
        product = offers_models.Product.query.filter_by(idAtProviders=movie_product_uuid).one_or_none()
        if product:
            return product
        product = offers_models.Product()
        product.idAtProviders = movie_product_uuid
        product.lastProviderId = provider_id
        product.subcategoryId = subcategories.SEANCE_CINE.id
        self.created_objects += 1
        return product

    def fill_product_attribut(
        self, product: offers_models.Product, event: ems_serializers.Event
    ) -> offers_models.Product:
        if event.title:
            product.name = event.title
        if event.synopsis:
            product.description = event.synopsis
        if event.duration:
            product.durationMinutes = event.duration
        product.dateModifiedAtLastProvider = datetime.datetime.utcnow()
        return product

    def get_or_create_offer(
        self, event: ems_serializers.Event, provider_id: int, venue: offerers_models.Venue
    ) -> offers_models.Offer:
        movie_offer_uuid = _build_movie_uuid_for_offer(event.allocine_id, venue.id)
        offer = offers_models.Offer.query.filter_by(idAtProvider=movie_offer_uuid).one_or_none()
        if offer:
            return offer
        offer = offers_models.Offer()
        offer.idAtProvider = movie_offer_uuid
        offer.lastProviderId = provider_id
        offer.subcategoryId = subcategories.SEANCE_CINE.id

        offer.venueId = venue.id
        offer.bookingEmail = venue.bookingEmail
        offer.withdrawalDetails = venue.withdrawalDetails
        self.created_objects += 1
        return offer

    def fill_offer_attribut(self, offer: offers_models.Offer, event: ems_serializers.Event) -> offers_models.Offer:
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
        session_stock_uuid = _build_session_uuid_for_stock(event.allocine_id, offer.venueId, session.id)
        stock = offers_models.Stock.query.filter_by(idAtProviders=session_stock_uuid).one_or_none()
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

        beginning_datetime = datetime.datetime.strptime(session.date, "%Y%m%d%H%M")
        stock.beginningDatetime = beginning_datetime
        stock.bookingLimitDatetime = beginning_datetime

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


def _build_session_uuid_for_stock(allocine_movie_id: int, venue_id: int, session_id: str) -> str:
    return f"{_build_movie_uuid_for_offer(allocine_movie_id, venue_id)}#{session_id}"


def _build_movie_uuid_for_offer(allocine_movie_id: int, venue_id: int) -> str:
    return f"{allocine_movie_id}%{venue_id}%EMS"


def _build_movie_uuid_for_product(allocine_movie_id: int) -> str:
    return f"{allocine_movie_id}%EMS"


def _get_movie_id_from_id_at_provider(id_at_provider: str) -> int:
    return int(id_at_provider.split("%")[0])
