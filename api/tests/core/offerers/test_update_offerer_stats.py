from unittest.mock import patch

import pytest
import time_machine

from pcapi.connectors.big_query.queries.offerer_stats import DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE
from pcapi.connectors.big_query.queries.offerer_stats import TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE
from pcapi.core.offerers import update_offerer_stats
from pcapi.core.offerers.factories import OffererFactory
from pcapi.core.offerers.factories import OffererStatsFactory
from pcapi.core.offerers.models import OffererStats
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class UpdateOffererStatsTest:
    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    def test_update_offerer_daily_views_stats(self, mock_run_query_with_params):
        offerer = OffererFactory()
        offerer2 = OffererFactory()

        OffererStatsFactory(
            offererId=offerer.id,
            syncDate="2023-10-14",
            table=DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            jsonData={
                "daily_views": [
                    {"numberOfViews": 10, "eventDate": "2023-10-14"},
                    {"numberOfViews": 7, "eventDate": "2023-10-13"},
                ]
            },
        )

        db.session.commit()

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {
                        "offererId": offerer.id,
                        "dailyViews": '[{"eventDate": "2023-10-16", "numberOfViews": 15}, {"eventDate": "2023-10-15", "numberOfViews": 10}, {"eventDate": "2023-10-14", "numberOfViews": 3}, {"eventDate": "2023-10-13", "numberOfViews": 2}]',
                    },
                    {
                        "offererId": offerer2.id,
                        "dailyViews": '[{"eventDate": "2023-10-13", "numberOfViews": 15}, {"eventDate": "2023-10-12", "numberOfViews": 10}, {"eventDate": "2023-10-11", "numberOfViews": 3}, {"eventDate": "2023-10-10", "numberOfViews": 2}]',
                    },
                ]
            ),
        ]
        update_offerer_stats.update_offerer_daily_views_stats()
        update_offerer_stats.delete_offerer_old_stats()

        new_offerer_stats = (
            db.session.query(OffererStats)
            .filter(
                OffererStats.table == DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            )
            .all()
        )

        assert len(new_offerer_stats) == 2
        assert new_offerer_stats[0].offererId == offerer.id
        assert new_offerer_stats[0].jsonData["daily_views"] == [
            {"eventDate": "2023-10-13", "numberOfViews": 2},
            {"eventDate": "2023-10-14", "numberOfViews": 3},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
            {"eventDate": "2023-10-16", "numberOfViews": 15},
        ]
        assert new_offerer_stats[1].offererId == offerer2.id
        assert new_offerer_stats[1].jsonData["daily_views"] == [
            {"eventDate": "2023-10-10", "numberOfViews": 2},
            {"eventDate": "2023-10-11", "numberOfViews": 3},
            {"eventDate": "2023-10-12", "numberOfViews": 10},
            {"eventDate": "2023-10-13", "numberOfViews": 15},
        ]

    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    def test_update_offerer_daily_views_stats_with_non_existing_offerer(self, mock_run_query_with_params):
        """This test checks that a non existing offerer does not break the stats synchronization.
        The data may still know about an offerer while it has been removed from the DB.
        This should just be ignored and should not break the whole data sync."""
        offerer = OffererFactory()
        offerer2 = OffererFactory()

        db.session.commit()

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {
                        "offererId": offerer.id,
                        "dailyViews": '[{"eventDate": "2023-10-16", "numberOfViews": 15}, {"eventDate": "2023-10-15", "numberOfViews": 10}, {"eventDate": "2023-10-14", "numberOfViews": 3}, {"eventDate": "2023-10-13", "numberOfViews": 2}]',
                    },
                    {
                        "offererId": 0,
                        "dailyViews": '[{"eventDate": "2023-10-16", "numberOfViews": 15}, {"eventDate": "2023-10-15", "numberOfViews": 10}, {"eventDate": "2023-10-14", "numberOfViews": 3}, {"eventDate": "2023-10-13", "numberOfViews": 2}]',
                    },
                    {
                        "offererId": offerer2.id,
                        "dailyViews": '[{"eventDate": "2023-10-13", "numberOfViews": 15}, {"eventDate": "2023-10-12", "numberOfViews": 10}, {"eventDate": "2023-10-11", "numberOfViews": 3}, {"eventDate": "2023-10-10", "numberOfViews": 2}]',
                    },
                ]
            ),
        ]
        assert update_offerer_stats.PAGE_SIZE > 1
        update_offerer_stats.update_offerer_daily_views_stats()

        new_offerer_stats = (
            db.session.query(OffererStats)
            .filter(
                OffererStats.table == DAILY_CONSULT_PER_OFFERER_LAST_180_DAYS_TABLE,
            )
            .all()
        )

        assert len(new_offerer_stats) == 2
        assert new_offerer_stats[0].offererId == offerer.id
        assert new_offerer_stats[0].jsonData["daily_views"] == [
            {"eventDate": "2023-10-13", "numberOfViews": 2},
            {"eventDate": "2023-10-14", "numberOfViews": 3},
            {"eventDate": "2023-10-15", "numberOfViews": 10},
            {"eventDate": "2023-10-16", "numberOfViews": 15},
        ]
        assert new_offerer_stats[1].offererId == offerer2.id
        assert new_offerer_stats[1].jsonData["daily_views"] == [
            {"eventDate": "2023-10-10", "numberOfViews": 2},
            {"eventDate": "2023-10-11", "numberOfViews": 3},
            {"eventDate": "2023-10-12", "numberOfViews": 10},
            {"eventDate": "2023-10-13", "numberOfViews": 15},
        ]

    @time_machine.travel("2023-10-25")
    @patch("pcapi.connectors.big_query.TestingBackend.run_query")
    def test_update_offerer_top_offers_stats(self, mock_run_query_with_params):
        offerer = OffererFactory()
        offerer2 = OffererFactory()

        offerer3 = OffererFactory()

        OffererStatsFactory(
            offererId=offerer3.id,
            syncDate="2023-10-14",
            table=TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            jsonData={
                "total_views": 50,
                "top_offers": [
                    {"numberOfViews": 7, "offerId": 1},
                    {"numberOfViews": 6, "offerId": 2},
                    {"numberOfViews": 4, "offerId": 3},
                ],
            },
        )

        db.session.commit()

        mock_run_query_with_params.side_effect = [
            iter(
                [
                    {
                        "offererId": offerer.id,
                        "topOffers": '[{"offerId": 1, "numberOfViews": 12}, {"offerId": 2, "numberOfViews": 10}, {"offerId": 3, "numberOfViews": 8}]',
                        "totalViews": 50,
                    },
                    {
                        "offererId": offerer2.id,
                        "topOffers": '[{"offerId": 1, "numberOfViews": 12}, {"offerId": 2, "numberOfViews": 10}]',
                        "totalViews": 22,
                    },
                ]
            ),
        ]

        update_offerer_stats.update_offerer_top_views_stats()
        update_offerer_stats.delete_offerer_old_stats()

        # Check that the stats have been updated

        new_offerer_stats = (
            db.session.query(OffererStats)
            .filter(
                OffererStats.table == TOP_3_MOST_CONSULTED_OFFERS_LAST_30_DAYS_TABLE,
            )
            .all()
        )
        assert len(new_offerer_stats) == 2
        assert new_offerer_stats[0].offererId == offerer.id
        assert new_offerer_stats[0].jsonData["top_offers"] == [
            {"offerId": 1, "numberOfViews": 12},
            {"offerId": 2, "numberOfViews": 10},
            {"offerId": 3, "numberOfViews": 8},
        ]
        assert new_offerer_stats[0].jsonData["total_views_last_30_days"] == 50
        assert new_offerer_stats[1].offererId == offerer2.id
        assert new_offerer_stats[1].jsonData["top_offers"] == [
            {"offerId": 1, "numberOfViews": 12},
            {"offerId": 2, "numberOfViews": 10},
        ]
