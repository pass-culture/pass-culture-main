import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


# TODO: Will be deleted in PR #24783 after native code deletion
class VenueProAdvicesTest:
    def test_returns_venue_pro_advices(self, client):
        offer = offers_factories.OfferFactory()
        venue_id = offer.venue.id
        pro_advice = offers_factories.ProAdviceFactory(offer=offer)
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        assert response.json == {
            "proAdvices": [
                {
                    "author": "Author",
                    "content": "Content",
                    "offerId": offer.id,
                    "offerName": offer.name,
                    "offerCategoryLabel": offer.subcategory.app_label,
                    "offerThumbUrl": offer.thumbUrl,
                    "publicationDatetime": date_utils.format_into_utc_date(pro_advice.updatedAt),
                }
            ],
            "nbResults": 1,
        }

    def test_returns_empty_list(self, client):
        with assert_num_queries(1):
            response = client.get("/native/v1/venue/99999999/advices")

        assert response.status_code == 200
        assert response.json == {"proAdvices": [], "nbResults": 0}

    def test_advices_are_ordered_by_recency(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _newer_advice = offers_factories.ProAdviceFactory(offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 2))
        _older_advice = offers_factories.ProAdviceFactory(offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 1))
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        first = response.json["proAdvices"][0]
        last = response.json["proAdvices"][1]
        assert first["publicationDatetime"] > last["publicationDatetime"]

    def test_author_can_be_null(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _pro_advice = offers_factories.ProAdviceFactory(offer__venue=venue, author=None)
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["author"] is None

    def test_trims_content(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _pro_advice = offers_factories.ProAdviceFactory(offer__venue=venue, content="very long content")
        params = {"maxContentLength": 8}
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["content"] == "very…"

    def test_returns_only_one_page(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        offers_factories.ProAdviceFactory.create_batch(size=2, offer__venue=venue)
        params = {"resultsPerPage": 1, "page": 1}
        expected_num_queries = 1  # pro_advices
        expected_num_queries = 2  # pro_advices count
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert len(response.json["proAdvices"]) == 1
        assert response.json["nbResults"] == 2

    def test_returns_requested_page(self, client):
        venue = offerers_factories.VenueFactory()
        venue_id = venue.id
        _newer_advice = offers_factories.ProAdviceFactory(
            offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 2), content="Page 1 content"
        )
        _older_advice = offers_factories.ProAdviceFactory(
            offer__venue=venue, updatedAt=datetime.datetime(2026, 2, 1), content="Page 2 content"
        )
        params = {"resultsPerPage": 1, "page": 2}
        expected_num_queries = 1  # pro_advices
        expected_num_queries = 2  # pro_advices count
        with assert_num_queries(expected_num_queries):
            response = client.get(f"/native/v1/venue/{venue_id}/advices", params=params)

        assert response.status_code == 200
        assert response.json["proAdvices"][0]["content"] == "Page 2 content"
        assert response.json["nbResults"] == 2

    def test_page_cannot_be_lt_1(self, client):
        params = {"page": 0, "resultsPerPage": 1}
        with assert_num_queries(0):
            response = client.get("/native/v1/venue/1/advices", params=params)

        assert response.status_code == 400

    def test_results_per_page_cannot_be_lt_1(self, client):
        params = {"page": 1, "resultsPerPage": 0}
        with assert_num_queries(0):
            response = client.get("/native/v1/venue/1/advices", params=params)

        assert response.status_code == 400

    def test_max_content_length_cannot_be_negative(self, client):
        params = {"maxContentLength": -1}
        with assert_num_queries(0):
            response = client.get("/native/v1/venue/1/advices", params=params)

        assert response.status_code == 400

    def test_does_not_return_unpublished_offer_advice(self, client):
        offer = offers_factories.OfferFactory(
            publicationDatetime=datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)
        )
        venue_id = offer.venue.id
        offers_factories.ProAdviceFactory(offer=offer)
        with assert_num_queries(1):
            response = client.get(f"/native/v1/venue/{venue_id}/advices")

        assert response.status_code == 200
        assert response.json == {"proAdvices": [], "nbResults": 0}
