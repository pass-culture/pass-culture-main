import datetime
import decimal

import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models import db

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class DeleteEventStockTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}/dates/{stock_id}"
    endpoint_method = "delete"
    default_path_params = {"event_id": 1, "stock_id": 2}

    def setup_base_resource(self, venue=None, provider=None) -> tuple[offers_models.Offer, offers_models.Stock]:
        event = offers_factories.EventOfferFactory(venue=venue or self.setup_venue(), lastProvider=provider)
        category_label = offers_factories.PriceCategoryLabelFactory(label="carre or", venue=event.venue)
        price_category = offers_factories.PriceCategoryFactory(
            offer=event, price=decimal.Decimal("88.99"), priceCategoryLabel=category_label
        )
        next_year = datetime.datetime.utcnow().replace(second=0, microsecond=0) + datetime.timedelta(days=365)
        stock = offers_factories.EventStockFactory(
            offer=event,
            quantity=10,
            price=12,
            priceCategory=price_category,
            bookingLimitDatetime=next_year,
            beginningDatetime=next_year,
        )

        return event, stock

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event, stock = self.setup_base_resource()
        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id)
        )
        assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id)
        )
        assert response.status_code == 404

    def test_delete_date(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
        )

        assert response.status_code == 204
        assert response.json is None
        assert stock.isSoftDeleted is True

    def test_delete_unbooked_date_with_ticket(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        # update event
        event.withdrawalType = WithdrawalTypeEnum.IN_APP
        db.session.commit()

        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id)
        )

        assert response.status_code == 204
        assert response.json is None
        assert stock.isSoftDeleted is True

    def test_stock_is_deleted_and_its_bookings_are_cancelled(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        bookings = bookings_factories.BookingFactory.create_batch(2, stock=stock)

        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id),
        )

        assert response.status_code == 204
        assert response.json is None
        assert stock.isSoftDeleted is True

        for booking in bookings:
            db.session.refresh(booking)
            assert booking.status == bookings_models.BookingStatus.CANCELLED

    def test_should_raise_400_if_event_stock_beginning_date_was_more_than_two_days_ago(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)

        # update
        event.withdrawalType = WithdrawalTypeEnum.IN_APP
        too_long_ago = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        stock.beginningDatetime = too_long_ago
        stock.bookingLimitDatetime = too_long_ago
        db.session.commit()

        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id)
        )

        assert response.status_code == 400
        assert response.json == {
            "global": ["L'évènement s'est terminé il y a plus de deux jours, la suppression est impossible."],
        }
        assert stock.isSoftDeleted is False

    def test_should_raise_404_if_already_soft_deleted(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event, stock = self.setup_base_resource(venue=venue_provider.venue, provider=venue_provider.provider)
        # update
        stock.isSoftDeleted = True
        db.session.commit()

        response = client.with_explicit_token(plain_api_key).delete(
            self.endpoint_url.format(event_id=event.id, stock_id=stock.id)
        )

        assert response.status_code == 404
        assert response.json == {"stock_id": ["No stock could be found"]}
