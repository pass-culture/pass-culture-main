import datetime
import logging

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offer_models
import pcapi.core.users.factories as users_factory
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class Returns204Test:
    def test_delete_headline_offer(self, client, caplog):
        pro = users_factory.ProFactory()
        offer = offers_factories.OfferFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offer.venue.managingOfferer)
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer)
        ten_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        old_headline_offer = offers_factories.HeadlineOfferFactory(offer=offer, timespan=(ten_days_ago, yesterday))

        data = {"offererId": offer.venue.managingOfferer.id}
        client = client.with_session_auth(pro.email)
        with caplog.at_level(logging.INFO):
            response = client.post("/offers/delete_headline", json=data)

        assert response.status_code == 204

        assert not headline_offer.isActive
        assert headline_offer.timespan.upper.date() == datetime.datetime.utcnow().date()
        assert not old_headline_offer.isActive
        assert old_headline_offer.timespan.upper == yesterday

        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 1
        log = next(log for log in caplog.records if log.message == "Headline Offer Deactivation")
        assert log.extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "Headline offer has been deactivated by user",
        }
        assert log.technical_message_id == "headline_offer_deactivation"

    def test_delete_only_offerers_headline_offer(self, client, caplog):
        pro = users_factory.ProFactory()
        offer = offers_factories.OfferFactory()
        offerer = offer.venue.managingOfferer
        another_offer = offers_factories.OfferFactory()
        another_offerer = another_offer.venue.managingOfferer
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer)
        another_headline_offer = offers_factories.HeadlineOfferFactory(offer=another_offer)

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        offerers_factories.UserOffererFactory(user=pro, offerer=another_offerer)
        client = client.with_session_auth(pro.email)
        data = {"offererId": offerer.id}
        with caplog.at_level(logging.INFO):
            response = client.post("/offers/delete_headline", json=data)

        assert response.status_code == 204

        assert not headline_offer.isActive
        assert another_headline_offer.isActive

        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 1
        log = next(log for log in caplog.records if log.message == "Headline Offer Deactivation")
        assert log.extra == {
            "analyticsSource": "app-pro",
            "HeadlineOfferId": headline_offer.id,
            "Reason": "Headline offer has been deactivated by user",
        }
        assert log.technical_message_id == "headline_offer_deactivation"


class Returns401Test:
    def test_delete_headline_when_current_user_has_no_rights_on_offer(self, client, caplog):
        pro = users_factory.ProFactory()
        offer = offers_factories.OfferFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offer.venue.managingOfferer)
        headline_offer = offers_factories.HeadlineOfferFactory(offer=offer)
        data = {"offererId": offer.venue.managingOfferer.id}

        response = client.post("/offers/delete_headline", json=data)

        assert response.status_code == 401

        assert db.session.query(offer_models.HeadlineOffer).count() == 1
        assert headline_offer.isActive

        assert len([log for log in caplog.records if log.message == "Headline Offer Deactivation"]) == 0
