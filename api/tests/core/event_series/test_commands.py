import logging
import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import exc as sa_exc

from pcapi.connectors.big_query.importer.event_series import EventSeriesImporter
from pcapi.connectors.big_query.importer.event_series import EventSeriesOfferLinkImporter
from pcapi.connectors.big_query.queries.artist import DeltaAction
from pcapi.connectors.big_query.queries.event_series import DeltaEventSeriesModel
from pcapi.connectors.big_query.queries.event_series import DeltaEventSeriesOfferLinkModel
from pcapi.core.event_series.factories import EventSeriesFactory
from pcapi.core.event_series.factories import EventSeriesOfferLinkFactory
from pcapi.core.event_series.models import EventSeries
from pcapi.core.event_series.models import EventSeriesOfferLink
from pcapi.core.offers.factories import OfferFactory
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.features(SYNCHRONIZE_EVENT_SERIES_FROM_BIGQUERY_TABLES=True)
class UpdateEventSeriesFromDeltaTest:
    @patch("pcapi.connectors.big_query.queries.event_series.EventSeriesDeltaQuery.execute")
    def test_updates_and_creates_event_series(self, mock_event_series_delta_query):
        series_to_delete_id = str(uuid.uuid4())
        _series_to_delete = EventSeriesFactory(id=series_to_delete_id, mediationUuid="old-uuid")
        new_series_id = str(uuid.uuid4())
        mock_event_series_delta_query.return_value = [
            DeltaEventSeriesModel(
                id=new_series_id,
                name="Nouvelle Série d'Événements",
                description="Description de la nouvelle série d'événements",
                mediation_uuid="new-uuid",
                action=DeltaAction.ADD,
            ),
            DeltaEventSeriesModel(id=series_to_delete_id, action=DeltaAction.REMOVE, name="Series to Delete"),
        ]

        EventSeriesImporter().run_delta_update()

        new_series = db.session.query(EventSeries).filter_by(id=new_series_id).first()
        assert db.session.query(EventSeries).filter_by(id=series_to_delete_id).first() is None
        assert db.session.query(EventSeries).count() == 1
        assert new_series is not None
        assert new_series.id == new_series_id
        assert new_series.name == "Nouvelle Série d'Événements"
        assert new_series.description == "Description de la nouvelle série d'événements"
        assert new_series.mediationUuid == "new-uuid"

    @patch("pcapi.connectors.big_query.queries.event_series.EventSeriesOfferLinkDeltaQuery.execute")
    def test_updates_and_creates_event_series_offer_links(self, mock_link_delta_query):
        series = EventSeriesFactory(id=str(uuid.uuid4()))
        offer = OfferFactory()
        offer2 = OfferFactory()

        link_to_delete = EventSeriesOfferLinkFactory(eventSeries=series, offerId=offer.id)
        link_to_delete_id = link_to_delete.id

        mock_link_delta_query.return_value = [
            DeltaEventSeriesOfferLinkModel(
                event_series_id=series.id,
                offer_id=offer2.id,
                action=DeltaAction.ADD,
            ),
            DeltaEventSeriesOfferLinkModel(
                event_series_id=series.id,
                offer_id=offer.id,
                action=DeltaAction.REMOVE,
            ),
        ]

        EventSeriesOfferLinkImporter().run_delta_update()

        assert (
            db.session.query(EventSeriesOfferLink).filter_by(eventSeriesId=series.id, offerId=offer2.id).first()
            is not None
        )
        assert db.session.query(EventSeriesOfferLink).filter_by(id=link_to_delete_id).first() is None
        assert db.session.query(EventSeriesOfferLink).count() == 1

    @patch("pcapi.connectors.big_query.queries.event_series.EventSeriesDeltaQuery.execute")
    def test_update_action_modifies_existing_event_series(self, mock_event_series_delta_query):
        series_to_update = EventSeriesFactory(id=str(uuid.uuid4()), name="Old Name", description="Old description")
        mediation_uuid = str(uuid.uuid4())
        mock_event_series_delta_query.return_value = [
            DeltaEventSeriesModel(
                id=series_to_update.id,
                name="New Name",
                description="New description",
                mediation_uuid=mediation_uuid,
                action=DeltaAction.UPDATE,
            ),
        ]

        EventSeriesImporter().run_delta_update()

        db.session.refresh(series_to_update)
        assert series_to_update.name == "New Name"
        assert series_to_update.description == "New description"
        assert series_to_update.mediationUuid == mediation_uuid

    @patch("pcapi.connectors.big_query.queries.event_series.EventSeriesDeltaQuery.execute")
    def test_update_action_does_nothing_for_non_existent_event_series(self, mock_event_series_delta_query):
        EventSeriesFactory(id=str(uuid.uuid4()))
        initial_series_count = db.session.query(EventSeries).count()
        non_existent_id = str(uuid.uuid4())
        mock_event_series_delta_query.return_value = [
            DeltaEventSeriesModel(id=non_existent_id, name="Série Fantôme", action=DeltaAction.UPDATE),
        ]

        EventSeriesImporter().run_delta_update()

        assert db.session.query(EventSeries).filter_by(id=non_existent_id).first() is None
        assert db.session.query(EventSeries).count() == initial_series_count

    @patch("pcapi.connectors.big_query.queries.event_series.EventSeriesDeltaQuery.execute")
    def test_update_event_series_batch_failure_triggers_retry(self, mock_event_series_delta_query, caplog):
        series1 = EventSeriesFactory(id=str(uuid.uuid4()), name="Old Name 1")
        series2 = EventSeriesFactory(id=str(uuid.uuid4()), name="Old Name 2")

        delta1 = DeltaEventSeriesModel(id=series1.id, name="New Name 1", action=DeltaAction.UPDATE)
        delta2 = DeltaEventSeriesModel(id=series2.id, name="New Name 2", action=DeltaAction.UPDATE)

        mock_event_series_delta_query.return_value = [delta1, delta2]

        with patch("pcapi.models.db.session.commit") as mock_commit:
            mock_commit.side_effect = [
                sa_exc.IntegrityError("Simulated Batch Integrity Error", params=None, orig=None),
                None,
                None,
            ]

            with caplog.at_level(logging.WARNING):
                EventSeriesImporter().run_delta_update(batch_size=2)

        assert "Batch update failed for EventSeries, retrying one by one" in caplog.text

        db.session.refresh(series1)
        db.session.refresh(series2)
        assert series1.name == "New Name 1"
        assert series2.name == "New Name 2"

    @patch("pcapi.core.event_series.commands.EventSeriesImporter.run_delta_update")
    @patch("pcapi.core.event_series.commands.EventSeriesOfferLinkImporter.run_delta_update")
    def test_update_command_runs_importers(
        self,
        mock_link_importer,
        mock_series_importer,
        run_command,
    ):
        run_command("update_event_series_from_delta", "--batch-size", "50")

        mock_series_importer.assert_called_once_with(50)
        mock_link_importer.assert_called_once_with(50)
