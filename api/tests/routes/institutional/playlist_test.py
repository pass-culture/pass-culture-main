import datetime

import pytest

from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import assert_num_queries
from pcapi.routes.shared.price import convert_to_cent


@pytest.mark.usefixtures("db_session")
class PlaylistTest:
    def test_get_playlist(self, client):
        not_tagged_offer = offers_factories.OfferFactory()
        offer_with_image = offers_factories.OfferFactory()
        mediation = offers_factories.MediationFactory(offer=offer_with_image)
        stock_with_image = offers_factories.StockFactory(offer=offer_with_image)
        offer_without_image = offers_factories.OfferFactory()
        stock_without_image = offers_factories.StockFactory(offer=offer_without_image)
        criterion = criteria_factories.CriterionFactory()
        criteria_factories.OfferCriterionFactory(offerId=offer_with_image.id, criterionId=criterion.id)
        criteria_factories.OfferCriterionFactory(offerId=offer_without_image.id, criterionId=criterion.id)

        criterion_name = criterion.name
        with assert_num_queries(1):
            response = client.get(f"/institutional/playlist/{criterion_name}")

        assert response.status_code == 200, response.json
        assert sorted(response.json, key=lambda offer: offer["id"]) == [
            {
                "id": offer_with_image.id,
                "image": {"credit": None, "url": mediation.thumbUrl},
                "name": offer_with_image.name,
                "stocks": [{"id": stock_with_image.id, "price": convert_to_cent(stock_with_image.price)}],
                "venue": {"id": offer_with_image.venue.id, "commonName": offer_with_image.venue.common_name},
            },
            {
                "id": offer_without_image.id,
                "image": None,
                "name": offer_without_image.name,
                "stocks": [{"id": stock_without_image.id, "price": convert_to_cent(stock_without_image.price)}],
                "venue": {"id": offer_without_image.venue.id, "commonName": offer_without_image.venue.common_name},
            },
        ]
        assert not_tagged_offer.id not in [offer["id"] for offer in response.json]

    def test_unreleased_offers_are_ignored(self, client):
        inactive_offer = offers_factories.OfferFactory(isActive=False)
        offers_factories.StockFactory(offer=inactive_offer)
        unvalidated_offer = offers_factories.EventOfferFactory(validation=offers_models.OfferValidationStatus.REJECTED)
        offers_factories.StockFactory(offer=unvalidated_offer)
        criterion = criteria_factories.CriterionFactory()
        criteria_factories.OfferCriterionFactory(offerId=inactive_offer.id, criterionId=criterion.id)
        criteria_factories.OfferCriterionFactory(offerId=unvalidated_offer.id, criterionId=criterion.id)

        response = client.get(f"/institutional/playlist/{criterion.name}")

        assert response.status_code == 200, response.json
        assert response.json == []

    def test_unbookable_offers_are_ignored(self, client):
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        unbookable_offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(offer=unbookable_offer, isSoftDeleted=True)
        offers_factories.EventStockFactory(offer=unbookable_offer, quantity=0)
        offers_factories.EventStockFactory(offer=unbookable_offer, beginningDatetime=yesterday)
        criterion = criteria_factories.CriterionFactory()
        criteria_factories.OfferCriterionFactory(offerId=unbookable_offer.id, criterionId=criterion.id)

        response = client.get(f"/institutional/playlist/{criterion.name}")

        assert response.status_code == 200, response.json
        assert response.json == []

    def test_unbookable_stocks_are_ignored(self, client):
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        offer = offers_factories.EventOfferFactory()
        offers_factories.EventStockFactory(offer=offer, isSoftDeleted=True)
        offers_factories.EventStockFactory(offer=offer, quantity=0)
        offers_factories.EventStockFactory(offer=offer, beginningDatetime=yesterday)
        bookable_stock = offers_factories.EventStockFactory(offer=offer)
        criterion = criteria_factories.CriterionFactory()
        criteria_factories.OfferCriterionFactory(offerId=offer.id, criterionId=criterion.id)

        response = client.get(f"/institutional/playlist/{criterion.name}")

        assert response.status_code == 200, response.json
        assert response.json == [
            {
                "id": offer.id,
                "image": None,
                "name": offer.name,
                "stocks": [{"id": bookable_stock.id, "price": convert_to_cent(bookable_stock.price)}],
                "venue": {"id": offer.venue.id, "commonName": offer.venue.common_name},
            }
        ]
