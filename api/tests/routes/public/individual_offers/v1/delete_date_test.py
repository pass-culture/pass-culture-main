import pytest

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers.models import WithdrawalTypeEnum

from . import utils


@pytest.mark.usefixtures("db_session")
class DeleteDateTest:
    def test_delete_date(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        stock_to_delete = offers_factories.EventStockFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{stock_to_delete.id}",
        )

        assert response.status_code == 204
        assert response.json is None
        assert stock_to_delete.isSoftDeleted is True

    def test_delete_unbooked_date_with_ticket(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(with_charlie=True)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            withdrawalType=WithdrawalTypeEnum.IN_APP,
        )
        stock_to_delete = offers_factories.EventStockFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{stock_to_delete.id}",
        )

        assert response.status_code == 204
        assert response.json is None
        assert stock_to_delete.isSoftDeleted is True

    def test_400_if_delete_date_with_booked_stock_from_charlie_api(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(with_charlie=True)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
            withdrawalType=WithdrawalTypeEnum.IN_APP,
        )
        stock_to_delete = offers_factories.EventStockFactory(offer=event_offer)
        bookings_factories.BookingFactory(quantity=1, stock=stock_to_delete)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{stock_to_delete.id}",
        )

        assert response.status_code == 400
        assert response.json == {
            "code": "STOCK_FROM_CHARLIE_API_CANNOT_BE_DELETED",
            "global": ["You can't delete a stock where bookings have tickets"],
        }
        assert stock_to_delete.isSoftDeleted is False

    def test_404_if_already_soft_deleted(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        already_deleted_stock = offers_factories.EventStockFactory(offer=event_offer, isSoftDeleted=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{already_deleted_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"date_id": ["The date could not be found"]}

    def test_404_if_others_offerer_offer(self, client):
        utils.create_offerer_provider_linked_to_venue()
        others_stock = offers_factories.EventStockFactory()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{others_stock.offerId}/dates/{others_stock.id}",
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}

    def test_404_if_inactive_venue_provider(self, client):
        venue, api_key = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            lastProvider=api_key.provider,
        )
        stock_to_delete = offers_factories.EventStockFactory(offer=event_offer)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).delete(
            f"/public/offers/v1/events/{event_offer.id}/dates/{stock_to_delete.id}",
        )

        assert response.status_code == 404
        assert response.json == {"event_id": ["The event could not be found"]}
