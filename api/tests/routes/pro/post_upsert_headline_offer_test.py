import datetime
import logging
from unittest import mock

import pytest

from pcapi.core import search
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import models as offers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_offer_headline(self, mocked_async_index_offer_ids, client, caplog):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        with caplog.at_level(logging.INFO):
            assert response.status_code == 201
        assert offer.is_headline_offer
        headline_offer = db.session.query(offers_models.HeadlineOffer).one()
        assert headline_offer

        assert response.json == {
            "id": headline_offer.offer.id,
            "image": {
                "credit": headline_offer.offer.image.credit,
                "url": headline_offer.offer.image.url,
            },
            "name": headline_offer.offer.name,
            "venueId": headline_offer.venue.id,
        }
        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 0

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_new_offer_headline(self, mocked_async_index_offer_ids, client, caplog):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(
            offer=offer,
            timespan=(
                datetime.datetime.utcnow() - datetime.timedelta(days=20),
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
            ),
        )
        assert not offer.is_headline_offer

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        with caplog.at_level(logging.INFO):
            response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 201
        assert offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 2
        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 0

        mocked_async_index_offer_ids.assert_called_once_with(
            {offer.id},
            reason=search.IndexationReason.OFFER_REINDEXATION,
        )

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_another_offer_headline(self, mocked_async_index_offer_ids, client, caplog):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        another_offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.MediationFactory(offer=another_offer)
        offers_factories.StockFactory(offer=another_offer)
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer)

        data = {
            "offerId": another_offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        with caplog.at_level(logging.INFO):
            response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 201

        assert not offer.is_headline_offer
        assert another_offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 2
        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 1
        log = next(log for log in caplog.records if log.message == "Headline Offer Deactivation")
        assert log.extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "User chose to replace this headline offer by another offer",
        }
        assert log.technical_message_id == "headline_offer_deactivation"

        expected_reindexation_calls = [
            mock.call({offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
            mock.call({another_offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
        ]
        mocked_async_index_offer_ids.assert_has_calls(expected_reindexation_calls)

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_another_offer_headline_when_first_offer_is_not_active_anymore(
        self, mocked_async_index_offer_ids, client, caplog
    ):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)
        another_offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.MediationFactory(offer=another_offer)
        offers_factories.StockFactory(offer=another_offer)
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer)

        data = {
            "offerId": another_offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        with caplog.at_level(logging.INFO):
            response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 201
        assert response.json["id"] == another_offer.id

        assert not offer.is_headline_offer
        assert another_offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 2
        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 1
        log = next(log for log in caplog.records if log.message == "Headline Offer Deactivation")
        assert log.extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "User chose to replace this headline offer by another offer",
        }
        assert log.technical_message_id == "headline_offer_deactivation"

        expected_reindexation_calls = [
            mock.call({offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
            mock.call({another_offer.id}, reason=search.IndexationReason.OFFER_REINDEXATION),
        ]
        mocked_async_index_offer_ids.assert_has_calls(expected_reindexation_calls)


class Returns400Test:

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_several_headline_offers_should_fail(self, mocked_async_index_offer_ids, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.HeadlineOfferFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Cette offre est déjà mise à la une"]

        assert offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).one()

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_make_inactive_offer_headline_should_fail(self, mocked_async_index_offer_ids, client):
        pro_user = users_factories.ProFactory()
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offerers_factories.UserOffererFactory(user=pro_user, offerer=venue.managingOfferer)
        offer = offers_factories.OfferFactory(venue=venue, isActive=False)
        offers_factories.StockFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Cette offre est inactive et ne peut pas être mise à la une"]

        assert not offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 0

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_ineligible_offerer_can_not_create_headline_offer(self, mocked_async_index_offer_ids, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offerers_factories.VenueFactory(isPermanent=False, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == [
            "Vous ne pouvez pas créer d'offre à la une sur une entité juridique possédant plusieurs structures"
        ]

        assert not offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 0

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_virtual_offer_can_not_be_headline(self, mocked_async_index_offer_ids, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offer = offers_factories.DigitalOfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)
        offers_factories.MediationFactory(offer=offer)

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Une offre virtuelle ne peut pas être mise à la une"]

        assert not offer.is_headline_offer
        assert db.session.query(offers_models.HeadlineOffer).count() == 0

        mocked_async_index_offer_ids.assert_not_called()

    @mock.patch("pcapi.core.search.async_index_offer_ids")
    def test_offer_without_image_can_not_be_headline(self, mocked_async_index_offer_ids, client):
        pro_user = users_factories.ProFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        venue = offerers_factories.VenueFactory(isPermanent=True, managingOfferer=offerer)
        offer = offers_factories.OfferFactory(venue=venue)
        offers_factories.StockFactory(offer=offer)

        assert not offer.images

        data = {
            "offerId": offer.id,
        }
        client = client.with_session_auth(pro_user.email)
        response = client.post("/offers/upsert_headline", json=data)

        assert response.status_code == 400
        assert response.json["global"] == ["Une offre doit avoir une image pour être mise à la une"]

        mocked_async_index_offer_ids.assert_not_called()
