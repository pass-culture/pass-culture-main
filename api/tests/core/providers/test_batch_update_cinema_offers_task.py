import datetime
import decimal

import pytest
import time_machine

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import batch_update_cinema_offers_task
from pcapi.core.providers import factories as provider_factories
from pcapi.core.providers import models as provider_models
from pcapi.models import db
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class BatchUpdateCinemaOffersTaskTest:
    def setup_base_resource(
        self,
    ) -> tuple[
        offerers_models.Venue,
        provider_models.Provider,
        offers_models.Product,
        offers_models.Product,
        geography_models.Address,
    ]:
        provider = provider_factories.PublicApiProviderFactory()
        venue = offerers_factories.VenueFactory()
        allocine_product = offers_factories.EventProductFactory(
            name="Juste une illusion", extraData={"allocineId": 1000015954}
        )
        visa_product = offers_factories.EventProductFactory(name="Hamnet", extraData={"visa": "166715"})
        address = geography_factories.AddressFactory()
        return venue, provider, allocine_product, visa_product, address

    def generate_task_payload(
        self,
        provider_id: int,
        venue_id: int,
        film_id: str | None = None,
        data: dict | None = None,
        address: dict | None = None,
    ) -> batch_update_cinema_offers_task.TaskPayload:
        two_weeks_from_now = date_utils.get_naive_utc_now().replace(
            hour=18, minute=30, second=0, microsecond=0
        ) + datetime.timedelta(weeks=2)
        request_payload = {
            "venueId": venue_id,
            "offers": [
                {
                    "address": address,
                    "filmId": film_id or "allocine_id:1000015954",
                    "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                    "stocks": [
                        {
                            "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                            "priceCategoryIdAtProvider": "PC",
                            "quantity": 100,
                            "idAtProvider": "film1234567_session1",
                            "features": ["VF"],
                        }
                    ],
                }
            ],
        }

        if data:
            request_payload.update(**data)

        return batch_update_cinema_offers_task.TaskPayload(provider_id=provider_id, request_payload=request_payload)

    @time_machine.travel("2026-05-01", tick=False)
    def test_create_offers_and_stocks_with_allocine(self):
        venue, provider, allocine_product, _, _ = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)
        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = db.session.query(offers_models.Stock).all()
        assert len(stocks) == 1

        offer = offers[0]
        price_category = price_categories[0]
        stock = stocks[0]

        assert offer.name == "Juste une illusion"
        assert offer.product == allocine_product
        assert offer.venue == venue
        assert offer.lastProvider == provider
        assert offer.idAtProvider == f"allocine_id:1000015954%{venue.id}"

        assert price_category.label == "Tarif pass Culture"
        assert price_category.price == decimal.Decimal("5.00")
        assert price_category.idAtProvider == "PC"

        assert stock.priceCategory == price_category
        assert stock.idAtProviders == "film1234567_session1"
        assert stock.features == ["VF"]
        assert stock.quantity == 100
        assert stock.beginningDatetime == datetime.datetime(2026, 5, 15, 18, 30)
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 5, 15, 18, 30)

    @time_machine.travel("2026-05-01", tick=False)
    def test_create_offer_with_visa(self):
        venue, provider, _, visa_product, _ = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id, film_id="visa:166715")
        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = db.session.query(offers_models.Stock).all()
        assert len(stocks) == 1

        offer = offers[0]

        assert offer.name == "Hamnet"
        assert offer.product == visa_product
        assert offer.venue == venue
        assert offer.lastProvider == provider
        assert offer.idAtProvider == f"visa:166715%{venue.id}"

    @time_machine.travel("2026-05-01", tick=False)
    def test_create_offer_at_specific_address(self):
        venue, provider, allocine_product, _, address = self.setup_base_resource()
        task_payload = self.generate_task_payload(
            provider_id=provider.id,
            venue_id=venue.id,
            address={"id": address.id, "label": "Somewhere out there"},
        )
        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = db.session.query(offers_models.Stock).all()
        assert len(stocks) == 1
        offerer_addresses = (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.addressId == address.id)
            .all()
        )
        assert len(offerer_addresses) == 1

        offerer_address = offerer_addresses[0]
        offer = offers[0]

        assert offer.name == "Juste une illusion"
        assert offer.product == allocine_product
        assert offer.venue == venue
        assert offer.lastProvider == provider
        assert offer.idAtProvider == f"allocine_id:1000015954%{venue.id}%{address.id}"
        assert offer.offererAddress == offerer_address

        assert offerer_address.label == "Somewhere out there"
        assert offerer_address.addressId == address.id
        assert offerer_address.type.value == "OFFER_LOCATION"

    @time_machine.travel("2026-05-01", tick=False)
    def test_task_is_idempotent(self):
        venue, provider, allocine_product, _, address = self.setup_base_resource()
        task_payload = self.generate_task_payload(
            provider_id=provider.id,
            venue_id=venue.id,
            address={"id": address.id, "label": "Somewhere out there"},
        )
        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)  # twice
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = db.session.query(offers_models.Stock).all()
        assert len(stocks) == 1
        offerer_addresses = (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.addressId == address.id)
            .all()
        )
        assert len(offerer_addresses) == 1

        offerer_address = offerer_addresses[0]
        offer = offers[0]
        price_category = price_categories[0]
        stock = stocks[0]

        assert offer.name == "Juste une illusion"
        assert offer.product == allocine_product
        assert offer.venue == venue
        assert offer.lastProvider == provider
        assert offer.idAtProvider == f"allocine_id:1000015954%{venue.id}%{address.id}"
        assert offer.offererAddress == offerer_address

        assert offerer_address.label == "Somewhere out there"
        assert offerer_address.addressId == address.id
        assert offerer_address.type.value == "OFFER_LOCATION"

        assert price_category.label == "Tarif pass Culture"
        assert price_category.price == decimal.Decimal("5.00")
        assert price_category.idAtProvider == "PC"

        assert stock.priceCategory == price_category
        assert stock.idAtProviders == "film1234567_session1"
        assert stock.features == ["VF"]
        assert stock.quantity == 100
        assert stock.beginningDatetime == datetime.datetime(2026, 5, 15, 18, 30)
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 5, 15, 18, 30)

    @time_machine.travel("2026-05-01", tick=False)
    def test_update_offer_and_stocks(self):
        venue, provider, allocine_product, _, _ = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)
        offer_to_update = offers_factories.OfferFactory(
            name="Juste une illusion",
            venue=venue,
            lastProvider=provider,
            product=allocine_product,
            idAtProvider=f"allocine_id:1000015954%{venue.id}",
        )
        price_category = offers_factories.PriceCategoryFactory(
            price=decimal.Decimal("6.00"),
            label="Tarif PC",
            offer=offer_to_update,
            idAtProvider="PC",
        )
        stock_to_update = offers_factories.StockFactory(
            offer=offer_to_update,
            idAtProviders="film1234567_session1",
            features=["VO", "3D"],
            quantity=130,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime(2026, 5, 16, 17, 15),
            bookingLimitDatetime=datetime.datetime(2026, 5, 16, 17, 15),
        )
        bookings_factories.BookingFactory(stock=stock_to_update)
        stock_to_update.dnBookedQuantity = 1
        db.session.commit()

        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = db.session.query(offers_models.Stock).all()
        assert len(stocks) == 1

        offer = offers[0]
        price_category = price_categories[0]
        stock = stocks[0]

        assert offer.name == "Juste une illusion"
        assert offer.product == allocine_product
        assert offer.venue == venue
        assert offer.lastProvider == provider
        assert offer.idAtProvider == f"allocine_id:1000015954%{venue.id}"

        assert price_category.label == "Tarif pass Culture"
        assert price_category.price == decimal.Decimal("5.00")
        assert price_category.idAtProvider == "PC"

        assert stock.priceCategory == price_category
        assert stock.idAtProviders == "film1234567_session1"
        assert stock.features == ["VF"]
        assert stock.quantity == 101
        assert stock.beginningDatetime == datetime.datetime(2026, 5, 15, 18, 30)
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 5, 15, 18, 30)

    @time_machine.travel("2026-05-01", tick=False)
    def test_update_offer_should_delete_removed_stock(self):
        venue, provider, allocine_product, _, _ = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)
        offer_to_update = offers_factories.OfferFactory(
            name="Juste une illusion",
            venue=venue,
            lastProvider=provider,
            product=allocine_product,
            idAtProvider=f"allocine_id:1000015954%{venue.id}",
        )
        price_category = offers_factories.PriceCategoryFactory(
            price=decimal.Decimal("6.00"),
            label="Tarif PC",
            offer=offer_to_update,
            idAtProvider="PC",
        )

        stock_to_delete = offers_factories.StockFactory(
            offer=offer_to_update,
            idAtProviders="film1234567_session2",
            features=["VO", "3D"],
            quantity=130,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime(2026, 5, 17, 17, 15),
            bookingLimitDatetime=datetime.datetime(2026, 5, 17, 17, 15),
        )
        stock_to_keep = offers_factories.StockFactory(  # in the past, should not be deleted
            offer=offer_to_update,
            idAtProviders="film1234567_session-5",
            features=["VO", "3D"],
            quantity=130,
            priceCategory=price_category,
            beginningDatetime=datetime.datetime(2026, 4, 1, 15, 15),
            bookingLimitDatetime=datetime.datetime(2026, 4, 1, 15, 15),
        )

        db.session.commit()

        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).all()
        assert len(offers) == 1
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 1
        stocks = (
            db.session.query(offers_models.Stock)
            .filter(
                offers_models.Stock.isSoftDeleted == False,
                offers_models.Stock.bookingLimitDatetime >= date_utils.get_naive_utc_now(),
            )
            .all()
        )
        assert len(stocks) == 1

        offer = offers[0]
        price_category = price_categories[0]
        stock = stocks[0]

        assert stock.priceCategory == price_category
        assert stock.idAtProviders == "film1234567_session1"
        assert stock.features == ["VF"]
        assert stock.quantity == 100
        assert stock.beginningDatetime == datetime.datetime(2026, 5, 15, 18, 30)
        assert stock.bookingLimitDatetime == datetime.datetime(2026, 5, 15, 18, 30)
        assert stock.offer == offer

        assert stock_to_delete.isSoftDeleted
        assert stock_to_delete.idAtProviders == "[DELETED:1777593600.0]film1234567_session2"

        assert not stock_to_keep.isSoftDeleted

    @time_machine.travel("2026-05-01", tick=False)
    def test_should_create_offer_with_same_film_id_on_different_location(self):
        venue, provider, _, visa_product, address = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)

        two_weeks_from_now = date_utils.get_naive_utc_now().replace(
            hour=18, minute=30, second=0, microsecond=0
        ) + datetime.timedelta(weeks=2)

        task_payload = batch_update_cinema_offers_task.TaskPayload(
            provider_id=provider.id,
            request_payload={
                "venueId": venue.id,
                "offers": [
                    {
                        "address": address,
                        "filmId": "visa:166715",
                        "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 100,
                                "idAtProvider": "film1234567_session1",
                                "features": ["VF"],
                            }
                        ],
                    },
                    {
                        "filmId": "visa:166715",
                        "priceCategories": [{"price": 600, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 50,
                                "idAtProvider": "film1234568_session2",
                                "features": ["VO"],
                            }
                        ],
                    },
                ],
            },
        )

        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).order_by(offers_models.Offer.id).all()
        assert len(offers) == 2
        price_categories = db.session.query(offers_models.PriceCategory).all()
        assert len(price_categories) == 2
        stocks = (
            db.session.query(offers_models.Stock)
            .filter(
                offers_models.Stock.isSoftDeleted == False,
                offers_models.Stock.bookingLimitDatetime >= date_utils.get_naive_utc_now(),
            )
            .all()
        )
        assert len(stocks) == 2

        offer_with_address = offers[0]
        offer_vanilla = offers[1]

        assert offer_with_address.product == visa_product
        assert offer_with_address.idAtProvider == f"visa:166715%{venue.id}%{address.id}"

        assert offer_vanilla.product == visa_product
        assert offer_vanilla.idAtProvider == f"visa:166715%{venue.id}"

    @time_machine.travel("2026-05-01", tick=False)
    def test_should_create_offer_should_not_duplicate_offerrer_address(self):
        venue, provider, _, visa_product, address = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)

        two_weeks_from_now = date_utils.get_naive_utc_now().replace(
            hour=18, minute=30, second=0, microsecond=0
        ) + datetime.timedelta(weeks=2)

        task_payload = batch_update_cinema_offers_task.TaskPayload(
            provider_id=provider.id,
            request_payload={
                "venueId": venue.id,
                "offers": [
                    {
                        "address": address,
                        "filmId": "visa:166715",
                        "priceCategories": [{"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 100,
                                "idAtProvider": "film1234567_session1",
                                "features": ["VO"],
                            }
                        ],
                    },
                    {
                        "address": address,
                        "filmId": "allocine_id:1000015954",
                        "priceCategories": [{"price": 600, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 50,
                                "idAtProvider": "film1234568_session2",
                                "features": ["VF"],
                            }
                        ],
                    },
                ],
            },
        )

        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).order_by(offers_models.Offer.id).all()
        assert len(offers) == 2
        offerer_addresses = (
            db.session.query(offerers_models.OffererAddress)
            .filter(offerers_models.OffererAddress.type == "OFFER_LOCATION")
            .all()
        )
        assert len(offerer_addresses) == 1

    @time_machine.travel("2026-05-01", tick=False)
    def test_should_create_offer_should_mapped_to_the_right_product_and_stock(self):
        venue, provider, allocine_product, visa_product, _ = self.setup_base_resource()
        task_payload = self.generate_task_payload(provider_id=provider.id, venue_id=venue.id)

        two_weeks_from_now = date_utils.get_naive_utc_now().replace(
            hour=18, minute=30, second=0, microsecond=0
        ) + datetime.timedelta(weeks=2)

        task_payload = batch_update_cinema_offers_task.TaskPayload(
            provider_id=provider.id,
            request_payload={
                "venueId": venue.id,
                "offers": [
                    {
                        "filmId": "visa:166715",
                        "priceCategories": [
                            {"price": 500, "label": "Tarif pass Culture", "idAtProvider": "PC"},
                            {"price": 1000, "label": "Tarif PC 2", "idAtProvider": "PC_2"},
                        ],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 100,
                                "idAtProvider": "film166715_session1",
                                "features": ["VF"],
                            },
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC_2",
                                "quantity": 200,
                                "idAtProvider": "film166715_session2",
                                "features": ["VO"],
                            },
                        ],
                    },
                    {
                        "filmId": "allocine_id:1000015954",
                        "priceCategories": [{"price": 600, "label": "Tarif pass Culture", "idAtProvider": "PC"}],
                        "stocks": [
                            {
                                "beginningDatetime": date_utils.format_into_utc_date(two_weeks_from_now),
                                "priceCategoryIdAtProvider": "PC",
                                "quantity": 50,
                                "idAtProvider": "film1000015954_session1",
                                "features": ["VF"],
                            }
                        ],
                    },
                ],
            },
        )

        batch_update_cinema_offers_task.batch_update_cinema_offers_task(task_payload)
        offers = db.session.query(offers_models.Offer).order_by(offers_models.Offer.id).all()
        assert len(offers) == 2

        offer_visa = offers[0]
        offer_allocine = offers[1]

        assert offer_visa.product == visa_product
        assert offer_visa.idAtProvider == f"visa:166715%{venue.id}"
        assert len(offer_visa.stocks) == 2
        assert len(offer_visa.priceCategories) == 2

        stock_vf = next(stock for stock in offer_visa.stocks if stock.features == ["VF"])
        assert stock_vf.quantity == 100
        assert stock_vf.idAtProviders == "film166715_session1"
        assert stock_vf.features == ["VF"]
        assert stock_vf.priceCategory.price == decimal.Decimal("5.00")
        assert stock_vf.priceCategory.label == "Tarif pass Culture"

        stock_vo = next(stock for stock in offer_visa.stocks if stock.features == ["VO"])
        assert stock_vo.quantity == 200
        assert stock_vo.idAtProviders == "film166715_session2"
        assert stock_vo.features == ["VO"]
        assert stock_vo.priceCategory.price == decimal.Decimal("10.00")
        assert stock_vo.priceCategory.label == "Tarif PC 2"

        assert offer_allocine.product == allocine_product
        assert offer_allocine.idAtProvider == f"allocine_id:1000015954%{venue.id}"

        assert len(offer_allocine.priceCategories) == 1
        assert offer_allocine.priceCategories[0].label == "Tarif pass Culture"
        assert offer_allocine.priceCategories[0].price == decimal.Decimal("6.00")

        assert len(offer_allocine.stocks) == 1
        assert offer_allocine.stocks[0].priceCategory == offer_allocine.priceCategories[0]
        assert offer_allocine.stocks[0].quantity == 50
        assert offer_allocine.stocks[0].features == ["VF"]
