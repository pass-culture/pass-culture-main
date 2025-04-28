import datetime
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import factories as dms_factories
from pcapi.connectors.dms import models as dms_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.api.dms import import_dms_applications
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models import db


DEFAULT_API_RESULT = [
    {
        "id": "RG9zc2llci0xMTcxNjExNw==",
        "number": 1,
        "archived": False,
        "state": "en_traitement",
        "dateDerniereModification": "2023-04-09T16:17:38+01:00",
        "dateDepot": "2023-03-06T16:17:37+01:00",
        "datePassageEnConstruction": "2023-03-07T16:17:37+01:00",
        "datePassageEnInstruction": "2023-04-08T16:17:37+01:00",
        "dateTraitement": "2023-04-09T16:19:37+01:00",
        "dateExpiration": "2024-03-06T16:17:37+01:00",
        "dateSuppressionParUsager": None,
        "demandeur": {"siret": "14171443600708"},
    },
    {
        "id": "RG9zc2llci0xMXcxNjExNw==",
        "number": 2,
        "archived": False,
        "state": "en_construction",
        "dateDerniereModification": "2023-03-06T16:17:38+01:00",
        "dateDepot": "2023-03-06T16:17:37+01:00",
        "datePassageEnConstruction": "2023-03-06T16:17:37+01:00",
        "datePassageEnInstruction": None,
        "dateTraitement": None,
        "dateExpiration": "2024-03-06T16:17:37+01:00",
        "dateSuppressionParUsager": None,
        "demandeur": {"siret": "50130899309201"},
    },
]


@pytest.mark.usefixtures("db_session")
class UpdateDmsStatusTest:
    def test_import_empty_db(self):
        venue1 = offerers_factories.VenueFactory(siret=DEFAULT_API_RESULT[0]["demandeur"]["siret"])
        venue2 = offerers_factories.VenueFactory(siret=DEFAULT_API_RESULT[1]["demandeur"]["siret"])
        mock = MagicMock()
        mock.get_eac_nodes_siret_states = MagicMock(return_value=DEFAULT_API_RESULT)
        with patch("pcapi.connectors.dms.api.DMSGraphQLClient", return_value=mock):
            import_dms_applications(procedure_number=123)
        mock.get_eac_nodes_siret_states.assert_called_once_with(
            procedure_number=123,
            since=None,
        )

        assert len(venue1.collectiveDmsApplications) == 1
        assert venue1.collectiveDmsApplications[0].state == "en_traitement"
        assert venue1.collectiveDmsApplications[0].procedure == 123
        assert venue1.collectiveDmsApplications[0].application == 1
        assert venue1.collectiveDmsApplications[0].siret == venue1.siret
        assert venue1.collectiveDmsApplications[0].lastChangeDate == datetime.datetime(2023, 4, 9, 15, 17, 38)
        assert venue1.collectiveDmsApplications[0].depositDate == datetime.datetime(2023, 3, 6, 15, 17, 37)
        assert venue1.collectiveDmsApplications[0].expirationDate == datetime.datetime(2024, 3, 6, 15, 17, 37)
        assert venue1.collectiveDmsApplications[0].buildDate == datetime.datetime(2023, 3, 7, 15, 17, 37)
        assert venue1.collectiveDmsApplications[0].instructionDate == datetime.datetime(2023, 4, 8, 15, 17, 37)
        assert venue1.collectiveDmsApplications[0].processingDate == datetime.datetime(2023, 4, 9, 15, 19, 37)
        assert venue1.collectiveDmsApplications[0].userDeletionDate is None

        assert len(venue2.collectiveDmsApplications) == 1
        assert venue2.collectiveDmsApplications[0].state == "en_construction"
        assert venue2.collectiveDmsApplications[0].procedure == 123
        assert venue2.collectiveDmsApplications[0].application == 2
        assert venue2.collectiveDmsApplications[0].siret == venue2.siret
        assert venue2.collectiveDmsApplications[0].lastChangeDate == datetime.datetime(2023, 3, 6, 15, 17, 38)
        assert venue2.collectiveDmsApplications[0].depositDate == datetime.datetime(2023, 3, 6, 15, 17, 37)
        assert venue2.collectiveDmsApplications[0].expirationDate == datetime.datetime(2024, 3, 6, 15, 17, 37)
        assert venue2.collectiveDmsApplications[0].buildDate == datetime.datetime(2023, 3, 6, 15, 17, 37)
        assert venue2.collectiveDmsApplications[0].instructionDate is None
        assert venue2.collectiveDmsApplications[0].processingDate is None
        assert venue2.collectiveDmsApplications[0].userDeletionDate is None

        latest_import = db.session.query(dms_models.LatestDmsImport).one()
        assert latest_import.procedureId == 123
        assert latest_import.latestImportDatetime is not None
        assert latest_import.isProcessing is False
        assert latest_import.processedApplications == [1, 2]

    def test_update_existing_data(self):
        venue = offerers_factories.VenueFactory(siret=DEFAULT_API_RESULT[0]["demandeur"]["siret"])

        educational_factories.CollectiveDmsApplicationFactory(
            venue=venue,
            application=DEFAULT_API_RESULT[0]["number"],
            procedure=123,
        )
        mock = MagicMock()
        mock.get_eac_nodes_siret_states = MagicMock(return_value=DEFAULT_API_RESULT)
        with patch("pcapi.connectors.dms.api.DMSGraphQLClient", return_value=mock):
            import_dms_applications(procedure_number=123)

        assert len(venue.collectiveDmsApplications) == 1
        assert venue.collectiveDmsApplications[0].state == "en_traitement"
        assert venue.collectiveDmsApplications[0].procedure == 123
        assert venue.collectiveDmsApplications[0].application == 1
        assert venue.collectiveDmsApplications[0].siret == venue.siret
        assert venue.collectiveDmsApplications[0].lastChangeDate == datetime.datetime(2023, 4, 9, 15, 17, 38)
        assert venue.collectiveDmsApplications[0].depositDate == datetime.datetime(2023, 3, 6, 15, 17, 37)
        assert venue.collectiveDmsApplications[0].expirationDate == datetime.datetime(2024, 3, 6, 15, 17, 37)
        assert venue.collectiveDmsApplications[0].buildDate == datetime.datetime(2023, 3, 7, 15, 17, 37)
        assert venue.collectiveDmsApplications[0].instructionDate == datetime.datetime(2023, 4, 8, 15, 17, 37)
        assert venue.collectiveDmsApplications[0].processingDate == datetime.datetime(2023, 4, 9, 15, 19, 37)
        assert venue.collectiveDmsApplications[0].userDeletionDate is None

    def test_only_call_from_last_update(self):
        mock = MagicMock()
        mock.get_eac_nodes_siret_states = MagicMock(return_value=DEFAULT_API_RESULT)

        previous = dms_factories.LatestDmsImportFactory(procedureId=123)

        with patch("pcapi.connectors.dms.api.DMSGraphQLClient", return_value=mock):
            import_dms_applications(procedure_number=123)
        mock.get_eac_nodes_siret_states.assert_called_once_with(
            procedure_number=123,
            since=previous.latestImportDatetime,
        )

    def test_only_process_if_previous_ended(self):
        mock = MagicMock()
        mock.get_eac_nodes_siret_states = MagicMock(return_value=DEFAULT_API_RESULT)

        dms_factories.LatestDmsImportFactory(
            procedureId=123,
            isProcessing=True,
        )

        with patch("pcapi.connectors.dms.api.DMSGraphQLClient", return_value=mock):
            import_dms_applications(procedure_number=123)
        mock.get_eac_nodes_siret_states.assert_not_called()

    def test_reset_import_if_stuck(self):
        mock = MagicMock()
        mock.get_eac_nodes_siret_states = MagicMock(return_value=DEFAULT_API_RESULT)

        latest_import = dms_factories.LatestDmsImportFactory(
            procedureId=123,
            isProcessing=True,
            latestImportDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )

        with patch("pcapi.connectors.dms.api.DMSGraphQLClient", return_value=mock):
            import_dms_applications(procedure_number=123)
        mock.get_eac_nodes_siret_states.assert_not_called()
        assert not latest_import.isProcessing
