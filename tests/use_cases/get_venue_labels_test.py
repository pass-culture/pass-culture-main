from unittest.mock import MagicMock

import pytest

from pcapi.domain.venue.venue_label.venue_label import VenueLabel
from pcapi.infrastructure.repository.venue.venue_label.venue_label_sql_repository import VenueLabelSQLRepository
from pcapi.use_cases.get_venue_labels import GetVenueLabels


class GetVenueLabelsTest:
    def setup_method(self):
        self.venue_label_repository = VenueLabelSQLRepository()
        self.venue_label_repository.get_all = MagicMock()
        self.get_venue_labels = GetVenueLabels(venue_label_repository=self.venue_label_repository)

    @pytest.mark.usefixtures("db_session")
    def test_should_return_the_list(self, app):
        # Given
        venue_labels = [
            VenueLabel(identifier=12, label="Maison des illustres"),
            VenueLabel(identifier=15, label="Monuments historiques"),
        ]
        self.venue_label_repository.get_all.return_value = venue_labels

        # When
        result = self.get_venue_labels.execute()

        # Then
        self.venue_label_repository.get_all.assert_called_once()
        assert result == venue_labels
