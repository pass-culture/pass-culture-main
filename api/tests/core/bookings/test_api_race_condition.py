import contextlib
import logging
import threading
from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import Stock
from pcapi.core.providers.factories import CDSCinemaDetailsFactory
from pcapi.core.providers.factories import CDSCinemaProviderPivotFactory
from pcapi.core.providers.factories import VenueProviderFactory
from pcapi.core.providers.models import Provider
from pcapi.core.providers.models import VenueProvider
from pcapi.local_providers.cinema_providers.cds.cds_stocks import CDSStocks
from pcapi.models import db

import tests.local_providers.cinema_providers.cds.fixtures as cds_fixtures


logger = logging.getLogger(__name__)


class BookingRaceConditionTest:
    def _setup(self, requests_mock, mock_get_venue_movies):
        cds_provider = db.session.query(Provider).filter(Provider.localClass == "CDSStocks").one()
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
        mocked_movies = [cds_fixtures.MOVIE_1]
        mock_get_venue_movies.return_value = mocked_movies

        requests_mock.get("https://example.com/coupez.png", content=bytes())

        requests_mock.get("https://account_id.fakeurl/shows?api_token=token", json=[cds_fixtures.SHOW_1])
        requests_mock.get(
            "https://account_id.fakeurl/vouchertype?api_token=token",
            json=[cds_fixtures.VOUCHER_TYPE_PC_1],
        )

        return venue_provider

    def assert_synchronization(self, cds_stocks):
        created_offers = db.session.query(Offer).order_by(Offer.id).all()
        assert len(created_offers) == 1
        created_stocks = db.session.query(Stock).order_by(Stock.id).all()
        assert len(created_stocks) == 1

        assert created_stocks[0].quantity == 77
        assert created_stocks[0].price == 5.0
        assert created_stocks[0].dateCreated is not None
        assert created_stocks[0].offer == created_offers[0]
        assert created_stocks[0].bookingLimitDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].beginningDatetime == datetime(2022, 6, 20, 9)
        assert created_stocks[0].features == ["VF", "3D"]

        assert cds_stocks.erroredObjects == 0
        assert cds_stocks.erroredThumbs == 0

    def get_scoped_session(self, app):
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        return Session

    def wait_for_booking_event_decorator(self, func, synchronization_event, booking_event):
        """
        Adding extra behavior to `fill_stocks_attribute`
        so we can wait for Booking thread to be executed
        before synchronization thread end.
        """

        def inner_func(*args, **kwargs):
            # At this point, `Stock` instance has been fetch
            # with a soon-to-be old dnBookedQuantity value
            # Pausing this thread and get into Booking one
            # so we can trigger race condition
            synchronization_event.set()
            logger.warning("synchronization_thread: waiting for booking thread to finish")
            booking_event.wait(timeout=2)
            logger.warning("synchronization_thread: after booking thread occured")
            result = func(*args, **kwargs)
            logger.warning("synchronization_thread: Successfully execute %s", str(func))
            return result

        return inner_func

    @contextlib.contextmanager
    def threadsafe_transaction(self, Session):
        """
        Transaction with a session local to each thread.
        """
        session = Session()
        try:
            yield session
            logger.warning("Successfully commit in a thread, session: %s", session)
            session.commit()
        except Exception:
            logger.warning("Rolling back in a thread, session: %s", session)
            session.rollback()
            raise
        finally:
            logger.warning("End of contextmanager, removing the session, session: %s", session)
            Session.remove()

    @pytest.mark.usefixtures("clean_database")
    @patch("pcapi.core.external_bookings.cds.client.CineDigitalServiceAPI.get_venue_movies")
    @patch("pcapi.settings.CDS_API_URL", "fakeUrl/")
    def test_stock_race_condition_between_booking_and_synchronization(self, mock_get_venue_movies, requests_mock, app):
        # Given
        logger.warning("main thread: Using scoped_session %s at %s", db.session, id(db.session))

        venue_provider = self._setup(requests_mock, mock_get_venue_movies)
        cds_stocks = CDSStocks(venue_provider=venue_provider)
        # First synchronization so we can have populated stocks
        cds_stocks.updateObjects()

        self.assert_synchronization(cds_stocks)
        first_stock_id = db.session.query(Stock).first().id

        synchronization_event = threading.Event()
        booking_event = threading.Event()

        def booking_thread(thread_local_session):
            """
            Mock a booking. We don’t have to do a real
            booking, everything we’re interested in
            is the `dnBookedQuantity` value which
            is updated after a successfull booking.
            Let’s do this.
            """
            with self.threadsafe_transaction(thread_local_session) as session:
                logger.warning("booking_thread: Using scoped_session %s at %s", session, id(session))
                # We always want for our synchronization_thread to start first.
                synchronization_event.wait()
                app.app_context().push()
                logger.warning("booking_thread: Before booking (should be after sync thread started)")
                logger.warning("booking_thread: Before update: stock_id: %s", first_stock_id)

                stock = session.query(Stock).filter(Stock.id == first_stock_id).with_for_update().one()

                logger.warning("Setting dnBookedQuantity of stock id: %s", stock.id)
                # Race condition occurs here, dnBookedQuantity value has been changed but
                # the session in synchronization_thread has no knowledge of it and
                # will commit an outdated value.
                stock.dnBookedQuantity = 1

                logger.warning("booking_thread: After update: stock_id: %s", first_stock_id)
                logger.warning("booking_thread: After booking")

        def sync_thread(thread_local_session):
            """
            We can’t pass cds_stocks.updateObjects to `threading.Thread`
            otherwise the session in CDSStocks would not be bound to this thread
            """
            with self.threadsafe_transaction(thread_local_session):
                logger.warning("synchronization_thread: Starting")
                app.app_context().push()
                venue_provider = db.session.query(VenueProvider).one()
                cds_stocks = CDSStocks(venue_provider=venue_provider)
                decorated_method = self.wait_for_booking_event_decorator(
                    cds_stocks.fill_stock_attributes, synchronization_event, booking_event
                )
                cds_stocks.fill_stock_attributes = decorated_method
                cds_stocks.updateObjects()
            self.assert_synchronization(cds_stocks)

        # Second synchronization during which we will have a race condition
        synchronization_thread = threading.Thread(target=sync_thread, args=[self.get_scoped_session(app)])
        booking_thread = threading.Thread(target=booking_thread, args=[self.get_scoped_session(app)])

        synchronization_thread.start()
        booking_thread.start()
        # Timeout to ensure we never endlessly wait for threads to end.
        # If we have to wait more than 5 seconds, something is wrong,
        # the test should be failing and be fixed.
        synchronization_thread.join(timeout=5)
        booking_thread.join(timeout=5)

        assert db.session.query(Stock).filter(Stock.id == first_stock_id).one().dnBookedQuantity == 1
