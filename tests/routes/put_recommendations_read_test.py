import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_recommendation
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_event_occurrence
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


RECOMMENDATION_URL = "/recommendations"


class Put:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_read_recommendations_are_given(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            user = create_user(email="test@email.com")
            event_occurrence1 = create_event_occurrence(offer)
            event_occurrence2 = create_event_occurrence(offer)
            stock1 = create_stock_from_event_occurrence(event_occurrence1, soft_deleted=True)
            stock2 = create_stock_from_event_occurrence(event_occurrence2, soft_deleted=False)
            thing_offer1 = create_offer_with_thing_product(venue)
            thing_offer2 = create_offer_with_thing_product(venue)
            stock3 = create_stock_from_offer(thing_offer1, soft_deleted=True)
            stock4 = create_stock_from_offer(thing_offer2, soft_deleted=False)
            recommendation1 = create_recommendation(offer, user)
            recommendation2 = create_recommendation(thing_offer1, user)
            recommendation3 = create_recommendation(thing_offer2, user)
            repository.save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

            read_recommendation_data = [
                {"dateRead": "2018-12-17T15:59:11.689000Z", "id": humanize(recommendation1.id)},
                {"dateRead": "2018-12-17T15:59:14.689000Z", "id": humanize(recommendation2.id)},
            ]

            # When
            response = (
                TestClient(app.test_client())
                .with_auth("test@email.com")
                .put("{}/read".format(RECOMMENDATION_URL), json=read_recommendation_data)
            )

            # Then
            read_recommendation_date_reads = [r["dateRead"] for r in response.json]
            assert len(read_recommendation_date_reads) == 2
            assert {"2018-12-17T15:59:11.689000Z", "2018-12-17T15:59:14.689000Z"} == set(read_recommendation_date_reads)
