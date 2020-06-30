from unittest.mock import patch

from scheduled_tasks.clock import pc_update_recommendations_view


class PcUpdateRecommendationsViewTest:
    @patch('scheduled_tasks.clock.feature_queries.is_active')
    @patch('scheduled_tasks.clock.discovery_view_queries.refresh')
    def test_should_call_refresh_view_when_recommendation_with_geolocation_is_not_active(self,
                                                                                         mock_discovery_refresh,
                                                                                         mock_feature,
                                                                                         app):
        # Given
        mock_feature.side_effect = [
            True, False
        ]

        # When
        pc_update_recommendations_view(app)

        # Then
        assert mock_feature.call_count == 2
        mock_discovery_refresh.assert_called_once()

    @patch('scheduled_tasks.clock.feature_queries.is_active')
    @patch('scheduled_tasks.clock.discovery_view_queries.refresh')
    def test_should_not_call_refresh_view_when_recommendation_with_geolocation_is_active(self,
                                                                                         mock_discovery_refresh,
                                                                                         mock_feature,
                                                                                         app):
        # Given
        mock_feature.side_effect = [
            True, True
        ]

        # When
        pc_update_recommendations_view(app)

        # Then
        assert mock_feature.call_count == 2
        mock_discovery_refresh.assert_not_called()
