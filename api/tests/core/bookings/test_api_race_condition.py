from datetime import datetime
import logging
import threading
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Product
from pcapi.core.offers.models import Stock
from pcapi.core.offers.models import VenueProvider
from pcapi.core.providers.factories import CDSCinemaDetailsFactory
from pcapi.core.providers.factories import CDSCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.models import db

from tests.conftest import clean_database
import tests.local_providers.cinema_providers.cds.fixtures as cds_fixtures

logger = logging.getLogger(__name__)



class BookingRaceConditionTest:
    def _setup(self, requests_mock, mock_get_venue_movies):
        cds_provider = Provider.query.filter(Provider.localClass == "CDSStocks").one()
        venue_provider = VenueProviderFactory(
            provider=cds_provider, isDuoOffers=True, venueIdAtOfferProvider="cinema_id_test"
        )
        cinema_provider_pivot = CDSCinemaProviderPivotFactory(
            venue=venue_provider.venue, idAtProvider=venue_provider.venueIdAtOfferProvider
        )
        CDSCinemaDetailsFactory(
            cinemaProviderPivot=cinema_provider_pivot, accountId="account_id", cinemaApiToken="token"
        )
        requests_mock.get(
            "https://account_id.fakeurl/cinemas?api_token=token",
            json=[cds_fixtures.CINEMA_WITH_INTERNET_SALE_GAUGE_ACTIVE_FALSE],
        )
        requests_mock.get("https://account_id.fakeurl/mediaoptions?api_token=token", json=cds_fixtures.MEDIA_OPTIONS)
        mocked_movies = [cds_fixtures.MOVIE_1, cds_fixtures.MOVIE_2]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())
        requests_mock.get("https://example.com/topgun.png", content=bytes())

        requests_mock.get(
            "https://account_id.fakeurl/shows?api_token=token", json=[cds_fixtures.SHOW_1, cds_fixtures.SHOW_2]
        )
        requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[cds_fixtures.VOUCHER_TYPE_PC_1, cds_fixtures.VOUCHER_TYPE_PC_2],
        )


        return venue_provider

    def assert_synchronization(self, cds_stocks):
        created_offers = Offer.query.order_by(Offer.id).all()
        assert len(created_offers) == 2
        created_products = Product.query.order_by(Product.id).all()
        assert len(created_products) == 2
        created_stocks = Stock.query.order_by(Stock.id).all()
        assert len(created_stocks) == 2

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].features == ["VF", "3D"]

        assert created_stocks[1].quantity == 78
        assert created_stocks[1].price == 6.5
        assert created_stocks[1].dateCreated is not None
        assert created_stocks[1].offer == created_offers[1]
        assert created_stocks[1].bookingLimitDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].beginningDatetime == datetime(2022, 7, 1, 10)
        assert created_stocks[1].features == []

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0


    def get_scoped_session(self, app):
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        return Session


    @clean_database
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_stock_race_condition_between_booking_and_synchronization(self, mock_get_venue_movies, requests_mock, app):
        # Given
        logger.warning("Using scoped_session %s at %s", db.session, id(db.session))

        venue_provider = self._setup(requests_mock, mock_get_venue_movies)
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        # First synchronization so we can have populated stocks
        cds_stocks.updateObjects()

        self.assert_synchronization(cds_stocks)
        first_stock = Stock.query.first()
        assert first_stock.dnBookedQuantity == 0

        synchronization_event = threading.Event()
        booking_event = threading.Event()

        def decorator_fill_stocks_attribute(func):
            """
            Adding extra behavior to `fill_stocks_attribute`
            so we can wait for Booking thread to be executed
            before synchronization thread end.
            """

            def inner_func(*args, **kwargs):
                synchronization_event.set()
                logger.warning("In synchronization_thread, waiting for booking thread to finish")
                booking_event.wait(timeout=5)
                logger.warning("In synchronization_thread, after booking thread occured")
                return func(*args, **kwargs)

            return inner_func

        @patch("pcapi.models.db.session", self.get_scoped_session(app))
        def booking():
            """
            Mock a booking. We don’t have to do a real
            booking, everything we’re interested in
            is the `dnBookedQuantity` value which
            is updated after a successfull booking.
            Let’s do this.
            """
            logger.warning("Using scoped_session %s at %s", db.session, id(db.session))
            synchronization_event.wait()
            app.app_context().push()
            logger.warning("In booking_thread before booking (should be after sync thread started)")
            logger.warning("booking_thread: stock_id: %s", first_stock.id)
            logger.warning("booking_thread: stock_dnBookedQuantity: %s", first_stock.dnBookedQuantity)
            db.session.query(Stock).filter(Stock.id == first_stock.id).update({"dnBookedQuantity": 1})
            logger.warning("booking_thread: After update: stock_id: %s", first_stock.id)
            logger.warning("booking_thread: After update: stock__dnBookedQuantity: %s", first_stock.dnBookedQuantity)
            logger.warning("In booking_thread after booking")
            db.session.commit()
            logger.warning(
                "Stock.id: %s updated to dnBookedQuantity: %s",
                first_stock.id,
                db.session.query(Stock).filter(Stock.id == first_stock.id).one().dnBookedQuantity,
            )
            booking_event.set()

        @patch("pcapi.models.db.session", self.get_scoped_session(app))
        def start_sync_thread():
            """
            We can’t pass cds_stocks.updateObjects to `threading.Thread`
            otherwise the session in CDSStocks would not be bound to the thread
            """
            logger.warning("Using scoped_session %s at %s", db.session, id(db.session))
            logger.warning("In start_sync_thread")
            app.app_context().push()
            venue_provider = VenueProvider.query.one()
            cds_stocks = CDSStocks(venue_provider=venue_provider)
            decorated_method = decorator_fill_stocks_attribute(cds_stocks.fill_stock_attributes)
            cds_stocks.fill_stock_attributes = decorated_method
            return cds_stocks.updateObjects()

        # Second synchronization during which we will have a race condition
        synchronization_thread = threading.Thread(target=start_sync_thread)
        booking_thread = threading.Thread(target=booking)

        synchronization_thread.start()
        booking_thread.start()

        synchronization_thread.join()
        booking_thread.join()

        self.assert_synchronization(cds_stocks)
        assert db.session.query(Stock).filter(Stock.id == first_stock.id).one().dnBookedQuantity == 1



