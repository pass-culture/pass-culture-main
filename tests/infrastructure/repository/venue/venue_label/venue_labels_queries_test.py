from typing import List

from domain.venue.venue_label.venue_label import VenueLabel
from infrastructure.repository.venue.venue_label.venue_label_sql_repository import VenueLabelSQLRepository
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_venue_label


class VenueLabelSQLRepositoryTest:
    def setup_method(self):
        self.venue_label_sql_repository = VenueLabelSQLRepository()

    @clean_database
    def test_should_return_the_venue_labels(self, app):
        # Given
        house = create_venue_label(idx=11, label='Maison des illustres')
        monuments = create_venue_label(idx=22, label='Monuments historiques')
        repository.save(house, monuments)
        expected_house_label = VenueLabel(identifier=11, label='Maison des illustres')
        expected_monuments_label = VenueLabel(identifier=22, label='Monuments historiques')

        # When
        venue_labels = self.venue_label_sql_repository.get_all()

        # Then
        assert len(venue_labels) == 2
        assert self._are_venue_label_present(expected_house_label, venue_labels)
        assert self._are_venue_label_present(expected_monuments_label, venue_labels)

    def _are_venue_label_present(self, expected_venue_label: VenueLabel, venue_labels: List[VenueLabel]) -> bool:
        for venue_label in venue_labels:
            if expected_venue_label.identifier == venue_label.identifier \
                    and expected_venue_label.label == venue_label.label:
                return True
        return False
