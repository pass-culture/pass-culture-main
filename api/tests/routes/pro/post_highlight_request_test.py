import datetime

import pytest

import pcapi.core.highlights.factories as highlights_factories
import pcapi.core.highlights.models as highlights_models
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.models import db
from pcapi.utils import db as db_utils


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_create_one_highlight_request_for_one_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        offer = offers_factories.OfferFactory()
        highlight = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.email)
        response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlights": [highlight.id]})

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 1
        assert highlight_request_query.one().offerId == offer.id
        assert highlight_request_query.one().highlightId == highlight.id

    def test_create_multiple_highlight_request_for_one_offer(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        offer = offers_factories.OfferFactory()
        highlight = highlights_factories.HighlightFactory()
        highlight2 = highlights_factories.HighlightFactory()

        client = client.with_session_auth(user_offerer.email)
        response = client.post(
            f"/offers/{offer.id}/highlight-requests", json={"highlights": [highlight.id, highlight2.id]}
        )

        assert response.status_code == 201

        highlight_request_query = db.session.query(highlights_models.HighlightRequest)
        assert highlight_request_query.count() == 2
        assert highlight_request_query.all()[0].offerId == offer.id
        assert highlight_request_query.all()[0].highlightId == highlight.id
        assert highlight_request_query.all()[1].offerId == offer.id
        assert highlight_request_query.all()[1].highlightId == highlight2.id


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_highlight_request_fail_if_highlight_is_not_available(self, client):
        user_offerer = offerers_factories.UserOffererFactory(user__email="user@example.com")
        offer = offers_factories.OfferFactory()
        now = datetime.datetime.now()
        highlight = highlights_factories.HighlightFactory(
            availability_timespan=db_utils.make_timerange(
                start=now - datetime.timedelta(days=10), end=now - datetime.timedelta(days=5)
            )
        )

        client = client.with_session_auth(user_offerer.email)
        response = client.post(f"/offers/{offer.id}/highlight-requests", json={"highlights": [highlight.id]})

        assert response.status_code == 400
