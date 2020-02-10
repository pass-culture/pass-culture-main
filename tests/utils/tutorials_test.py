from unittest.mock import patch

from models import Mediation
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_offerer, create_venue, create_mediation
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.tutorials import _upsert_tuto_mediation


class UpsertTutoMediationTest:
    class WhenNoTutoMediationTest:
        @patch('utils.tutorials.create_thumb')
        @clean_database
        def test_calls_create_thumb_once_when_has_no_back_and_saves_mediation(self, create_thumb_mock, app):
            # Given
            create_thumb_mock.return_value = Mediation()

            # When
            _upsert_tuto_mediation(0, has_back=False)

            # Then
            create_thumb_mock.assert_called_once()
            assert Mediation.query.filter_by(tutoIndex=0).count() == 1

        @patch('utils.tutorials.create_thumb')
        @clean_database
        def test_calls_create_thumb_once_when_has_back_and_saves_mediation(self, create_thumb_mock, app):
            # Given
            create_thumb_mock.return_value = Mediation()

            # When
            _upsert_tuto_mediation(1, has_back=True)

            # Then
            assert create_thumb_mock.call_count == 2
            assert Mediation.query.filter_by(tutoIndex=1).count() == 1

    class WhenExistingTutoMediationTest:
        @patch('utils.tutorials.create_thumb')
        @clean_database
        def test_does_not_call_create_thumb(self, create_thumb_mock, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            mediation = create_mediation(offer, tuto_index=0)
            repository.save(mediation)

            # When
            _upsert_tuto_mediation(0)

            # Then
            create_thumb_mock.assert_not_called()
