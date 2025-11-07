import datetime
import logging

import pytest

import pcapi.core.highlights.factories as highlights_factories
import pcapi.core.highlights.models as highlights_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models import db
from pcapi.utils import db as db_utils


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_one_highlight_request_for_one_offer(self, client, caplog):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with caplog.at_level(logging.INFO):
            response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight.id]})

        assert response.status_code == 201
        response_json = response.json
        assert response_json["id"] == offer.id
        assert len(response_json["highlightRequests"]) == 1
        assert response_json["highlightRequests"][0]["id"] == highlight.id

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 1
        assert highlight_request_query.one().offerId == offer.id
        assert highlight_request_query.one().highlightId == highlight.id

        assert len([log for log in caplog.records if log.message == "Highlight requests have been created"]) == 1
        log = next(log for log in caplog.records if log.message == "Highlight requests have been created")
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "highlight_ids": [highlight.id],
        }

        assert len([log for log in caplog.records if log.message == "Highlight requests have been deleted"]) == 0

        assert log.technical_message_id == "offer.highlightRequests.created"

    def test_create_multiple_highlight_requests_for_one_offer(self, client, caplog):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()
        highlight2 = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with caplog.at_level(logging.INFO):
            response = client.post(
                f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight.id, highlight2.id]}
            )

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest).order_by(
            highlights_models.HighlightRequest.id
        )
        assert highlight_request_query.count() == 2
        assert highlight_request_query.all()[0].offerId == offer.id
        assert highlight_request_query.all()[0].highlightId == highlight.id
        assert highlight_request_query.all()[1].offerId == offer.id
        assert highlight_request_query.all()[1].highlightId == highlight2.id

        assert len([log for log in caplog.records if log.message == "Highlight requests have been created"]) == 1
        log = next(log for log in caplog.records if log.message == "Highlight requests have been created")
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "highlight_ids": [highlight.id, highlight2.id],
        }

        assert log.technical_message_id == "offer.highlightRequests.created"

    def test_create_highlight_request_for_offer_already_having_request_on_this_highlight(self, client, caplog):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight)

        client = client.with_session_auth(user_offerer.user.email)
        with caplog.at_level(logging.INFO):
            response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight.id]})

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 1
        assert highlight_request_query.one().offerId == offer.id
        assert highlight_request_query.one().highlightId == highlight.id

        assert len([log for log in caplog.records if log.message == "Highlight requests have been created"]) == 0

    def test_update_highlight_request_with_new_list(self, client, caplog):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()
        highlight2 = highlights_factories.HighlightFactory()
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight)
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight2)

        highlight3 = highlights_factories.HighlightFactory()
        highlight4 = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.user.email)
        with caplog.at_level(logging.INFO):
            response = client.post(
                f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight3.id, highlight4.id]}
            )

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 2
        assert highlight_request_query.filter(highlights_models.HighlightRequest.offerId == offer.id).count() == 2
        assert (
            highlight_request_query.filter(highlights_models.HighlightRequest.highlightId == highlight3.id).count() == 1
        )
        assert (
            highlight_request_query.filter(highlights_models.HighlightRequest.highlightId == highlight4.id).count() == 1
        )

        assert len([log for log in caplog.records if log.message == "Highlight requests have been created"]) == 1
        log = next(log for log in caplog.records if log.message == "Highlight requests have been created")
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "highlight_ids": [highlight3.id, highlight4.id],
        }

        assert log.technical_message_id == "offer.highlightRequests.created"

    def test_empty_list_should_delete_current_highlight_requests_but_keep_past_ones(self, client, caplog):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()
        highlight2 = highlights_factories.HighlightFactory()

        now = datetime.datetime.now()
        unavailable_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=now - datetime.timedelta(days=10), end=now - datetime.timedelta(days=5)
            )
        )
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight)
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=highlight2)
        highlights_factories.HighlightRequestFactory(offer=offer, highlight=unavailable_highlight)

        client = client.with_session_auth(user_offerer.user.email)
        with caplog.at_level(logging.INFO):
            response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": []})

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 1
        assert highlight_request_query.one().offerId == offer.id
        assert highlight_request_query.one().highlightId == unavailable_highlight.id

        assert len([log for log in caplog.records if log.message == "Highlight requests have been deleted"]) == 1
        log = next(log for log in caplog.records if log.message == "Highlight requests have been deleted")
        assert log.extra == {
            "offer_id": offer.id,
            "venue_id": offer.venueId,
            "highlight_ids": [highlight.id, highlight2.id],
        }

        assert log.technical_message_id == "offer.highlightRequests.deleted"

        assert len([log for log in caplog.records if log.message == "Highlight requests have been created"]) == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_highlight_request_should_fail_if_highlight_is_not_available(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()

        now = datetime.datetime.now()
        unavailable_highlight = highlights_factories.HighlightFactory(
            availability_datespan=db_utils.make_inclusive_daterange(
                start=now - datetime.timedelta(days=10), end=now - datetime.timedelta(days=5)
            )
        )

        client = client.with_session_auth(user_offerer.user.email)
        response = client.post(
            f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [unavailable_highlight.id, highlight.id]}
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Un des temps fort n'est pas disponible"]

    def test_highlight_request_should_fail_if_one_highlight_is_not_known(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.EventOfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.post(
            f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight.id + 1, highlight.id]}
        )

        assert response.status_code == 400
        assert response.json["global"] == ["Un des temps fort n'existe pas"]

    def test_highlight_request_should_fail_if_offer_is_not_event(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        offer = offers_factories.OfferFactory(venue=venue)

        highlight = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.user.email)
        response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlight_ids": [highlight.id]})

        assert response.status_code == 400
        assert response.json["global"] == [
            "La sous catégorie de l'offre ne lui permet pas de participer à un temps fort"
        ]
