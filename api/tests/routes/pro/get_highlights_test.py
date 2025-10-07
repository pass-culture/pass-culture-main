from datetime import timedelta

import pytest

from pcapi.core import testing
from pcapi.core.highlights import factories as highlights_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.utils import db as db_utils
from pcapi.utils.date import get_naive_utc_now


pytestmark = pytest.mark.usefixtures("db_session")

num_queries = testing.AUTHENTICATION_QUERIES
num_queries += 1


def test_get_highlights_list(client):
    available_highlights = highlights_factories.HighlightFactory.create_batch(2)
    highlights_factories.HighlightFactory(
        availability_timespan=db_utils.make_timerange(
            start=get_naive_utc_now() + timedelta(days=10),
            end=get_naive_utc_now() + timedelta(days=11),
        ),
        highlight_timespan=db_utils.make_timerange(
            start=get_naive_utc_now() + timedelta(days=12),
            end=get_naive_utc_now() + timedelta(days=13),
        ),
    )
    highlights_factories.HighlightFactory(
        availability_timespan=db_utils.make_timerange(
            start=get_naive_utc_now() - timedelta(days=10),
            end=get_naive_utc_now() - timedelta(days=9),
        )
    )
    user_offerer = offerers_factories.UserOffererFactory()

    auth_client = client.with_session_auth(email=user_offerer.user.email)
    with testing.assert_num_queries(num_queries):
        response = auth_client.get("/highlights")
        assert response.status_code == 200
    assert response.json == [
        {
            "id": available_highlights[0].id,
            "name": available_highlights[0].name,
            "description": available_highlights[0].description,
            "availabilityTimespan": [
                available_highlights[0].availability_timespan.lower.isoformat() + "Z",
                available_highlights[0].availability_timespan.upper.isoformat() + "Z",
            ],
            "highlightTimespan": [
                available_highlights[0].highlight_timespan.lower.isoformat() + "Z",
                available_highlights[0].highlight_timespan.upper.isoformat() + "Z",
            ],
            "mediationUrl": available_highlights[0].mediation_url,
        },
        {
            "id": available_highlights[1].id,
            "name": available_highlights[1].name,
            "description": available_highlights[1].description,
            "availabilityTimespan": [
                available_highlights[1].availability_timespan.lower.isoformat() + "Z",
                available_highlights[1].availability_timespan.upper.isoformat() + "Z",
            ],
            "highlightTimespan": [
                available_highlights[1].highlight_timespan.lower.isoformat() + "Z",
                available_highlights[1].highlight_timespan.upper.isoformat() + "Z",
            ],
            "mediationUrl": available_highlights[1].mediation_url,
        },
    ]
