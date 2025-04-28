import pytest

from pcapi.core.offerers.models import VenueLabel
from pcapi.models import db
from pcapi.scripts.venue.venue_label.create_venue_labels import save_new_venue_labels


class SaveNewVenueLabelsTest:
    @pytest.mark.usefixtures("db_session")
    def test_should_save_venue_labels_to_database(self):
        # Given
        venue_labels_to_create = [
            ("Architecture contemporaine remarquable", 1),
            ("CAC - Centre d'art contemporain d'intérêt national", 2),
        ]

        # When
        save_new_venue_labels(venue_labels_to_create)

        # Then
        venue_labels_sql_entities = db.session.query(VenueLabel).all()
        assert len(venue_labels_sql_entities) == 2
        assert "Architecture contemporaine remarquable" in [
            venue_label.label for venue_label in venue_labels_sql_entities
        ]
        assert "CAC - Centre d'art contemporain d'intérêt national" in [
            venue_label.label for venue_label in venue_labels_sql_entities
        ]
