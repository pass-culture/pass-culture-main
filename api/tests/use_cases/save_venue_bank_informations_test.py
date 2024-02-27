from base64 import b64encode
from datetime import datetime
from datetime import timedelta
from unittest.mock import call
from unittest.mock import patch

import flask
import pytest
import schwifty

from pcapi import settings
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.serializer import ApplicationDetailOldJourney
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.ds import update_ds_applications_for_procedure
import pcapi.core.finance.factories as finance_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import override_features
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.models.api_errors import ApiErrors
from pcapi.models.feature import Feature
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformationsFactory
from pcapi.utils.urls import build_pc_pro_venue_link

import tests.connector_creators.demarches_simplifiees_creators as dms_creators


pytestmark = pytest.mark.usefixtures("db_session")


class SaveVenueBankInformationsTest:
    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    class GetReferentVenueTest:
        def setup_method(self):
            SaveVenueBankInformationsV4 = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations_v4 = SaveVenueBankInformationsV4(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_v4_raises_an_error_if_dms_token_is_absent(self, mock_update_text_annotation):
            application_details = ApplicationDetailOldJourney(
                application_type=4,
                status=GraphQLApplicationStates.accepted.value,
                application_id=1,
                dossier_id="2",
                iban="XXX",
                bic="YYY",
                updated_at=datetime.utcnow().isoformat(),
                dms_token=None,
                error_annotation_id="Q2hhbXAtOTE1NDg5",
                venue_url_annotation_id=None,
            )

            self.save_venue_bank_informations_v4.get_referent_venue(
                application_details,
            )
            assert self.save_venue_bank_informations_v4.api_errors.errors["Venue"] == ["Venue not found"]

        def test_v4_raises_an_error_if_no_venue_found_by_dms_token(self, mock_update_text_annotation):
            application_details = ApplicationDetailOldJourney(
                application_type=4,
                status=GraphQLApplicationStates.accepted.value,
                application_id=1,
                dossier_id="2",
                iban="XXX",
                bic="YYY",
                updated_at=datetime.utcnow().isoformat(),
                dms_token="1234567890abcdef",
                error_annotation_id="Q2hhbXAtOTE1NDg5",
                venue_url_annotation_id=None,
            )

            self.save_venue_bank_informations_v4.get_referent_venue(
                application_details,
            )
            assert self.save_venue_bank_informations_v4.api_errors.errors["Venue"] == ["Venue not found"]

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class SaveBankInformationV4ProcedureTest:
        def setup_method(self):
            SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_draft_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(pricing_point="self")
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.draft.value, dms_token=venue.dmsToken
            )

            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == finance_models.BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_draft_application_without_dms_token(self, mock_archive_dossier, mock_update_text_annotation):
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.draft.value, dms_token=""
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            assert finance_models.BankInformation.query.count() == 0

        def test_on_going_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(pricing_point="self")
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.on_going.value, dms_token=venue.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == finance_models.BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_accepted_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(pricing_point="self")
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
            assert venue.current_reimbursement_point_id == venue.id
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_refused_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(pricing_point="self")
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.refused.value, dms_token=venue.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == finance_models.BankInformationStatus.REJECTED
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_without_continuation_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(pricing_point="self")
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.without_continuation.value, dms_token=venue.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == finance_models.BankInformationStatus.REJECTED
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class UpdateBankInformationV4ProcedureTest:
        def setup_method(self):
            SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_update_bank_info_with_new_iban_bic(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue_with_accpeted_bank_info = offerers_factories.VenueFactory(pricing_point="self")
            bank_information = finance_factories.BankInformationFactory(
                applicationId=8,
                bic="SCROOGEBANK",
                iban="FR8888888888888888888888888",
                venue=venue_with_accpeted_bank_info,
            )
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                application_id=bank_information.applicationId, dms_token=venue_with_accpeted_bank_info.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.offererId is None
            assert bank_information.venueId == venue_with_accpeted_bank_info.id
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_update_bank_info_with_draft_application(self, mock_archive_dossier, mock_update_text_annotation, app):
            venue_with_accpeted_bank_info = offerers_factories.VenueFactory(pricing_point="self")
            finance_factories.BankInformationFactory(
                bic="SCROOGEBANK",
                iban="FR8888888888888888888888888",
                venue=venue_with_accpeted_bank_info,
                status=finance_models.BankInformationStatus.DRAFT,
            )
            application_raw_data = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.on_going.value, dms_token=venue_with_accpeted_bank_info.dmsToken
            )
            data = parse_raw_bank_info_data(application_raw_data, 4)

            self.save_venue_bank_informations.execute(
                application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data})
            )

            bank_information = finance_models.BankInformation.query.one()
            assert bank_information.venue == venue_with_accpeted_bank_info
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == finance_models.BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_when_overriding_another_bank_information_should_raise(
            self, mock_archive_dossier, mock_update_text_annotation, app
        ):
            venue = offerers_factories.VenueFactory(
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            finance_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
            )
            other_venue = offerers_factories.VenueFactory(
                siret="79387501912345",
                managingOfferer__siren="793875019",
            )
            finance_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=other_venue,
            )
            duplicate_bank_info = dms_creators.get_bank_info_response_procedure_v4(
                state=GraphQLApplicationStates.on_going.value, dms_token=other_venue.dmsToken, application_id=8
            )
            duplicate_bank_info["champs"][3]["value"] = "NL36INGB2682297498"

            data = parse_raw_bank_info_data(duplicate_bank_info, 4)

            # When
            with pytest.raises(ApiErrors) as errors:
                self.save_venue_bank_informations.execute(
                    application_details=ApplicationDetailOldJourney(**{"application_type": 4, **data}),
                )

            # Then
            bank_information_count = finance_models.BankInformation.query.count()
            assert bank_information_count == 2
            assert errors.value.errors['"venueId"'] == [
                "Une entrée avec cet identifiant existe déjà dans notre base de données"
            ]
            mock_archive_dossier.assert_not_called()

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    class SaveBankInformationUpdateTextOnErrorTest:
        application_id = "1"
        annotation_id = "Q4hhaXAtOEE1NSg5"
        dossier_id = "Q4zzaXAtOEE1NSg5"

        def setup_method(self):
            SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def build_application_detail(self, updated_field=None):
            application_data = {
                "siren": "999999999",
                "application_type": 4,
                "status": GraphQLApplicationStates.accepted.value,
                "application_id": self.application_id,
                "dossier_id": self.dossier_id,
                "iban": "FR7630007000111234567890144",
                "bic": "SOGEFRPP",
                "updated_at": datetime.utcnow().isoformat(),
                "venue_name": "venuedemo",
                "error_annotation_id": self.annotation_id,
                "venue_url_annotation_id": None,
                "dms_token": "1234567890abcdef",
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetailOldJourney(**application_data)

        def test_update_text_venue_not_found(self, mock_update_text_annotation, app):
            application_details = self.build_application_detail()

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            mock_update_text_annotation.assert_called_once_with(
                dossier_id=self.dossier_id, annotation_id=self.annotation_id, message="Venue: Venue not found"
            )

        def test_update_text_application_details_older_than_saved(self, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(dateModified=datetime.utcnow(), venue=venue)
            yesterday = datetime.utcnow() - timedelta(days=1)
            application_details = self.build_application_detail(
                {"dms_token": venue.dmsToken, "updated_at": yesterday.isoformat()}
            )

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            mock_update_text_annotation.assert_called_once_with(
                dossier_id=self.dossier_id,
                annotation_id=self.annotation_id,
                message="BankInformation: Received application details are older than saved one",
            )

        def test_update_text_application_details_has_more_advanced_status(self, mock_update_text_annotation, app):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.ACCEPTED)
            application_details = self.build_application_detail(
                {"dms_token": venue.dmsToken, "status": GraphQLApplicationStates.draft}
            )

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            mock_update_text_annotation.assert_called_once_with(
                dossier_id=self.dossier_id,
                annotation_id=self.annotation_id,
                message="BankInformation: Received dossier is in draft state. Move it to 'Accepté' to save it.",
            )

        def test_update_text_application_details_is_rejected_status(self, mock_update_text_annotation, app):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.ACCEPTED)
            application_details = self.build_application_detail(
                {"dms_token": venue.dmsToken, "status": GraphQLApplicationStates.refused}
            )

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            mock_update_text_annotation.assert_called_once_with(
                dossier_id=self.dossier_id,
                annotation_id=self.annotation_id,
                message="BankInformation: Received application details state does not allow to change bank information",
            )

        def test_update_text_application_details_on_bank_information_error(self, mock_update_text_annotation, app):
            venue = offerers_factories.VenueFactory(name="venuedemo")
            application_details = self.build_application_detail({"dms_token": venue.dmsToken, "iban": "INVALID"})

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            mock_update_text_annotation.assert_called_once_with(
                dossier_id=self.dossier_id,
                annotation_id=self.annotation_id,
                message='iban: L’IBAN renseigné ("INVALID") est invalide',
            )

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class SaveBankInformationUpdateTextTest:
        def setup_method(self):
            SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def build_application_detail(self, updated_field=None):
            application_data = {
                "siren": "999999999",
                "siret": "36252187900034",
                "status": GraphQLApplicationStates.accepted.value,
                "application_id": 1,
                "dossier_id": "DOSSIER_ID",
                "iban": "FR7630007000111234567890144",
                "bic": "SOGEFRPP",
                "updated_at": datetime.utcnow().isoformat(),
                "venue_name": "venuedemo",
                "error_annotation_id": "ANNOTATION_ID",
                "venue_url_annotation_id": None,
                "dms_token": "1234567890abcdef",
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetailOldJourney(**{"application_type": 4, **application_data})

        def test_update_text_annotation_and_archive_on_validated_bank_information(
            self, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(name="venuedemo", pricing_point="self", dmsToken="1234567890abcdef")
            application_details = self.build_application_detail()

            self.save_venue_bank_informations.execute(application_details=application_details)

            bank_information_count = finance_models.BankInformation.query.count()
            assert bank_information_count == 1
            mock_update_text_annotation.assert_called_once_with(
                dossier_id="DOSSIER_ID",
                annotation_id="ANNOTATION_ID",
                message="Dossier successfully imported",
            )
            mock_archive_dossier.assert_called_once_with("DOSSIER_ID")

        def test_archive_dossier_on_refused_bank_information(
            self, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(name="venuedemo", dmsToken="1234567890abcdef")
            application_details = self.build_application_detail({"status": GraphQLApplicationStates.refused.value})
            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            bank_information_count = finance_models.BankInformation.query.count()
            assert bank_information_count == 1
            mock_archive_dossier.assert_called_once_with("DOSSIER_ID")

        def test_update_text_application_details_on_draft_bank_information(
            self, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(name="venuedemo", dmsToken="1234567890abcdef")
            application_details = self.build_application_detail({"status": GraphQLApplicationStates.draft.value})

            self.save_venue_bank_informations.execute(
                application_details=application_details,
            )

            bank_information_count = finance_models.BankInformation.query.count()
            assert bank_information_count == 1
            mock_update_text_annotation.assert_called_once_with(
                dossier_id="DOSSIER_ID",
                annotation_id="ANNOTATION_ID",
                message="Valid dossier",
            )
            mock_archive_dossier.assert_not_called()


@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
@patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
@patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
class DSV4InOldBankInformationsJourneyTest:
    application_id = "2674321"
    b64_encoded_application_id = "Q2zzbXAtNzgyODAw"
    dms_token = "1234567890abcdef"

    def setup_method(self):
        SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DS_BANK_ACCOUNT_PROCEDURE_ID)
        self.save_venue_bank_informations = SaveVenueBankInformations(
            venue_repository=VenueWithBasicInformationSQLRepository(),
            bank_informations_repository=BankInformationsSQLRepository(),
        )

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_creation_and_association_bank_information_to_a_venue_in_DSv4_context(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        venue = offerers_factories.VenueFactory(pricing_point="self", dmsToken=self.dms_token)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with(self.b64_encoded_application_id)
        mock_update_text_annotation.assert_any_call(
            dossier_id=self.b64_encoded_application_id,
            annotation_id="Q2hhbXAtOTE1NDg5",
            message="Dossier successfully imported",
        )
        mock_update_text_annotation.assert_any_call(
            self.b64_encoded_application_id, "Q2hhbXAtMjc1NzMyOQ==", build_pc_pro_venue_link(venue)
        )
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_should_prepend_annotation_if_any_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        venue = offerers_factories.VenueFactory(pricing_point="self", dmsToken=self.dms_token)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value,
            annotations=[
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Quelque chose ne va pas",
                    "value": "Quelque chose ne va pas",
                },
                {"id": "Q2hhbXAtMjc1NzMyOQ==", "label": "URL du lieu", "stringValue": "", "value": None},
            ],
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with(self.b64_encoded_application_id)
        mock_update_text_annotation.assert_any_call(
            dossier_id=self.b64_encoded_application_id,
            annotation_id="Q2hhbXAtOTE1NDg5",
            message="Dossier successfully imported, Quelque chose ne va pas",
        )
        mock_update_text_annotation.assert_any_call(
            self.b64_encoded_application_id, "Q2hhbXAtMjc1NzMyOQ==", build_pc_pro_venue_link(venue)
        )
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_should_not_write_same_message_annotation_twice(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        venue = offerers_factories.VenueFactory(pricing_point="self", dmsToken=self.dms_token)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value,
            annotations=[
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Dossier successfully imported, Quelque chose ne va pas",
                    "value": "Dossier successfully imported, Quelque chose ne va pas",
                },
                {"id": "Q2hhbXAtMjc1NzMyOQ==", "label": "URL du lieu", "stringValue": "", "value": None},
            ],
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with(self.b64_encoded_application_id)
        mock_update_text_annotation.assert_called_once_with(
            self.b64_encoded_application_id, "Q2hhbXAtMjc1NzMyOQ==", build_pc_pro_venue_link(venue)
        )
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_should_not_rewrite_url_venue_if_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        venue = offerers_factories.VenueFactory(pricing_point="self", dmsToken=self.dms_token)
        venue_url = build_pc_pro_venue_link(venue)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value,
            annotations=[
                {
                    "id": "Q2hhbXAtOTE1NDg5",
                    "label": "Erreur traitement pass Culture",
                    "stringValue": "Dossier successfully imported, Quelque chose ne va pas",
                    "value": "Dossier successfully imported",
                },
                {"id": "Q2hhbXAtMjc1NzMyOQ==", "label": "URL du lieu", "stringValue": venue_url, "value": None},
            ],
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with(self.b64_encoded_application_id)
        mock_update_text_annotation.assert_not_called()
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()


@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
@patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
@patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
class DSV5InOldBankInformationsJourneyTest:
    application_id = "14742654"
    b64_encoded_application_id = "RG9zc2llci0xNDc0MjY1NA=="

    def setup_method(self):
        SaveVenueBankInformations = SaveVenueBankInformationsFactory.get(settings.DS_BANK_ACCOUNT_PROCEDURE_ID)
        self.save_venue_bank_informations = SaveVenueBankInformations(
            venue_repository=VenueWithBasicInformationSQLRepository(),
            bank_informations_repository=BankInformationsSQLRepository(),
        )

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_creation_and_association_bank_information_to_a_venue_in_DSv5_context(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic is None
        assert bank_information.iban is None
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT
        mock_archive_dossier.assert_not_called()
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_association_to_physical_venue_if_both_virtual_and_physical_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VirtualVenueFactory(managingOfferer=venue.managingOfferer)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic is None
        assert bank_information.iban is None
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT
        mock_archive_dossier.assert_not_called()
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_updated_status_successfully_update_bank_informations(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic is None
        assert bank_information.iban is None
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT
        mock_archive_dossier.assert_not_called()

        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_called_once_with(self.b64_encoded_application_id)
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_bank_information_is_not_linked_to_a_venue_if_many_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert bank_information.offerer == venue.managingOfferer
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        mock_archive_dossier.assert_not_called()
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_updated_status_successfully_update_bank_informations_when_attach_to_an_offerer(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert bank_information.bic is None
        assert bank_information.iban is None
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT
        mock_archive_dossier.assert_not_called()

        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        # New journey is not active, should not create BankAccount nor links
        assert not finance_models.BankAccount.query.count()
        assert not offerers_models.VenueBankAccountLink.query.count()


@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
@patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
@patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
class NewBankAccountJourneyTest:
    dsv4_application_id = 9
    dsv5_application_id = 14742654

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv4_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_has_calls([call("Q2zzbXAtNzgyODAw"), call("Q2zzbXAtNzgyODAw")])

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0

    @pytest.mark.parametrize("ff_activated", [True, False])
    def test_v4_stop_using_bank_informations_and_bank_account_if_rejected(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, ff_activated
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        with override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=ff_activated):
            update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        link = offerers_models.VenueReimbursementPointLink.query.one()
        assert link.venue == venue
        assert link.reimbursementPoint == venue
        assert link.timespan.upper is None

        if ff_activated:
            # New journey
            bank_account = finance_models.BankAccount.query.one()
            assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
            bank_account_link = offerers_models.VenueBankAccountLink.query.one()
            assert bank_account_link.venue == venue
            assert bank_account_link.bankAccount == bank_account
            assert bank_account_link.timespan.upper is None

        ### For compliance reasons, the DS application might be set to rejected, even if accepted before. ###

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.refused.value, dms_token=venue.dmsToken
        )
        with override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=ff_activated):
            update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.status == finance_models.BankInformationStatus.REJECTED
        link = offerers_models.VenueReimbursementPointLink.query.one()
        assert link.venue == venue
        assert link.reimbursementPoint == venue
        assert link.timespan.upper is not None

        if ff_activated:
            # New journey
            bank_account = finance_models.BankAccount.query.one()
            assert bank_account.status == finance_models.BankAccountApplicationStatus.REFUSED
            bank_account_link = offerers_models.VenueBankAccountLink.query.one()
            assert bank_account_link.venue == venue
            assert bank_account_link.bankAccount == bank_account
            assert bank_account_link.timespan.upper is not None

    @pytest.mark.parametrize("ff_activated", [True, False])
    def test_v5_stop_using_bank_informations_and_bank_account_if_rejected(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, ff_activated
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        with override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=ff_activated):
            update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        link = offerers_models.VenueReimbursementPointLink.query.one()
        assert link.venue == venue
        assert link.reimbursementPoint == venue
        assert link.timespan.upper is None

        if ff_activated:
            # New journey
            bank_account = finance_models.BankAccount.query.one()
            assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED

            bank_account_link = offerers_models.VenueBankAccountLink.query.one()
            assert bank_account_link.venue == venue
            assert bank_account_link.bankAccount == bank_account
            assert bank_account_link.timespan.upper is None

        ### For compliance reasons, the DS application might be set to rejected, even if accepted before. ###

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.refused.value,
        )
        with override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=ff_activated):
            update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.status == finance_models.BankInformationStatus.REJECTED

        link = offerers_models.VenueReimbursementPointLink.query.one()
        assert link.venue == venue
        assert link.reimbursementPoint == venue
        assert link.timespan.upper is not None

        if ff_activated:
            # New journey
            bank_account = finance_models.BankAccount.query.one()
            assert bank_account.status == finance_models.BankAccountApplicationStatus.REFUSED

            bank_account_link = offerers_models.VenueBankAccountLink.query.one()
            assert bank_account_link.venue == venue
            assert bank_account_link.bankAccount == bank_account
            assert bank_account_link.timespan.upper is not None

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv4_link_is_created_if_several_venues_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        venue_without_bank_account_but_also_with_only_free_offer = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        venue_with_no_bank_account = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        offers_factories.StockFactory(offer__venue=venue_with_no_bank_account)
        offers_factories.StockFactory(offer__venue=venue_without_bank_account_but_also_with_only_free_offer, price=0)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_has_calls([call("Q2zzbXAtNzgyODAw"), call("Q2zzbXAtNzgyODAw")])

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == venue_with_no_bank_account.bookingEmail

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_creating_DSv4_with_aldready_existing_link_should_deprecate_old_one_and_create_new_one(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        bank_account = finance_factories.BankAccountFactory(offerer=venue.managingOfferer)
        soon_to_be_deprecated_link = offerers_factories.VenueBankAccountLinkFactory(
            bankAccount=bank_account, venue=venue, timespan=(datetime.utcnow(),)
        )
        venue_with_no_bank_account = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        venue_without_non_free_offer = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        offerer = venue.managingOfferer
        offers_factories.StockFactory(offer__venue=venue_with_no_bank_account)
        offers_factories.StockFactory(offer__venue=venue_without_non_free_offer, price=0)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_accounts = sorted(finance_models.BankAccount.query.all(), key=lambda b: b.id)
        assert len(bank_accounts) == 2
        bank_account = bank_accounts[1]
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = sorted(offerers_models.VenueBankAccountLink.query.all(), key=lambda v: v.id)
        assert len(bank_account_link) == 2

        mock_archive_dossier.assert_has_calls([call("Q2zzbXAtNzgyODAw"), call("Q2zzbXAtNzgyODAw")])

        old_link = bank_account_link[0]
        new_link = bank_account_link[1]

        assert old_link == soon_to_be_deprecated_link
        assert old_link.timespan.upper
        assert new_link.venue == venue
        assert new_link.bankAccount == bank_account
        assert not new_link.timespan.upper

        assert history_models.ActionHistory.query.count() == 2  # One link deprecated and one created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == venue_with_no_bank_account.bookingEmail

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv4_bank_account_get_successfully_updated_on_status_change(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.on_going.value, dms_token=venue.dmsToken
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert not bank_information.bic
        assert not bank_information.iban
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == venue.name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        mock_archive_dossier.assert_not_called()

        assert not offerers_models.VenueBankAccountLink.query.count()

        assert not history_models.ActionHistory.query.count()
        on_going_status_history = finance_models.BankAccountStatusHistory.query.one()

        assert on_going_status_history.status == bank_account.status
        assert on_going_status_history.timespan.upper is None

        # DS dossier status is updated by the compliance (accepted)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )

        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.name
        mock_archive_dossier.assert_has_calls([call("Q2zzbXAtNzgyODAw"), call("Q2zzbXAtNzgyODAw")])

        assert offerers_models.VenueBankAccountLink.query.count() == 1

        assert history_models.ActionHistory.query.count() == 1
        status_history = finance_models.BankAccountStatusHistory.query.order_by(
            finance_models.BankAccountStatusHistory.id
        ).all()
        assert len(status_history) == 2
        accepted_status_history = status_history[-1]

        db_session.refresh(on_going_status_history)
        db_session.refresh(bank_account)

        assert on_going_status_history.timespan.upper is not None
        assert (
            accepted_status_history.status
            == bank_account.status
            == finance_models.BankAccountApplicationStatus.ACCEPTED
        )
        assert accepted_status_history.timespan.upper is None

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv5_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_has_calls([call("RG9zc2llci0xNDc0MjY1NA=="), call("RG9zc2llci0xNDc0MjY1NA==")])

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv5_link_is_not_created_if_several_venues_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        second_venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)
        _third_venue_without_non_free_offer = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer=venue.managingOfferer
        )
        offers_factories.StockFactory(offer__venue=venue)
        offers_factories.StockFactory(offer__venue=second_venue)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert not offerers_models.VenueBankAccountLink.query.count()

        assert not history_models.ActionHistory.query.count()
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 2
        assert {mails_testing.outbox[0]["To"], mails_testing.outbox[1]["To"]} == {
            venue.bookingEmail,
            second_venue.bookingEmail,
        }

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_draft_dossier_are_not_archived(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert not bank_information.bic
        assert not bank_information.iban
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.DRAFT
        assert bank_account.label == "Intitulé du compte bancaire"
        assert not bank_account.venueLinks
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not offerers_models.VenueBankAccountLink.query.count()
        assert not history_models.ActionHistory.query.count()

        assert finance_models.BankAccountStatusHistory.query.count() == 1

        assert len(mails_testing.outbox) == 0

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_on_going_dossier_are_not_archived(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert not bank_information.bic
        assert not bank_information.iban
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not offerers_models.VenueBankAccountLink.query.count()

        assert not history_models.ActionHistory.query.count()
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_DSv5_bank_account_get_successfully_updated_on_status_change(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert not bank_information.bic
        assert not bank_information.iban
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not offerers_models.VenueBankAccountLink.query.count()
        assert not history_models.ActionHistory.query.count()

        on_going_status_history = finance_models.BankAccountStatusHistory.query.one()

        assert on_going_status_history.status == bank_account.status
        assert on_going_status_history.timespan.upper is None

        # DS dossier status is updated by the compliance (accepted)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        mock_archive_dossier.assert_has_calls([call("RG9zc2llci0xNDc0MjY1NA=="), call("RG9zc2llci0xNDc0MjY1NA==")])

        link = offerers_models.VenueBankAccountLink.query.one()
        assert link.bankAccount == bank_account
        assert link.venue == venue

        assert history_models.ActionHistory.query.count() == 1
        status_history = finance_models.BankAccountStatusHistory.query.order_by(
            finance_models.BankAccountStatusHistory.id
        ).all()
        assert len(status_history) == 2
        accepted_status_history = status_history[-1]

        db_session.refresh(on_going_status_history)
        db_session.refresh(bank_account)

        assert on_going_status_history.timespan.upper is not None
        assert (
            accepted_status_history.status
            == bank_account.status
            == finance_models.BankAccountApplicationStatus.ACCEPTED
        )
        assert accepted_status_history.timespan.upper is None

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_dsv5_with_no_status_changes_does_not_create_nor_link_nor_status_changes_logs(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        link = offerers_models.VenueBankAccountLink.query.one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert history_models.ActionHistory.query.count() == 1
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        # Multiple crons running without any changes

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        link = offerers_models.VenueBankAccountLink.query.one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert history_models.ActionHistory.query.count() == 1
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_offerer_can_have_several_bank_informations(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer=venue.managingOfferer)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert not bank_information.venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert not offerers_models.VenueBankAccountLink.query.count()

        assert not history_models.ActionHistory.query.count()
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        fake_bic = str(schwifty.BIC.from_bank_code("FR", bank_code="30004"))
        fake_iban = str(schwifty.IBAN.generate("FR", bank_code="30004", account_code="12345"))

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
            b64_encoded_application_id=b64encode("Champ-123".encode()),
            application_id=123,
            bic=fake_bic,
            iban=fake_iban,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        # Old journey
        bank_informations = finance_models.BankInformation.query.order_by(finance_models.BankInformation.id).all()
        assert len(bank_informations) == 2
        assert not bank_informations[0].venue
        assert bank_informations[0].bic == "BICAGRIFRPP"
        assert bank_informations[0].iban == "FR7630006000011234567890189"
        assert bank_informations[0].status == finance_models.BankInformationStatus.ACCEPTED

        assert not bank_informations[1].venue
        assert bank_informations[1].bic == fake_bic
        assert bank_informations[1].iban == fake_iban
        assert bank_informations[1].status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_accounts = finance_models.BankAccount.query.order_by(finance_models.BankAccount.id).all()
        assert len(bank_accounts) == 2
        assert bank_accounts[0].bic == "BICAGRIFRPP"
        assert bank_accounts[0].iban == "FR7630006000011234567890189"
        assert bank_accounts[0].offerer == venue.managingOfferer
        assert bank_accounts[0].status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_accounts[0].label == "Intitulé du compte bancaire"
        assert bank_accounts[0].dsApplicationId == self.dsv5_application_id

        assert bank_accounts[1].bic == fake_bic
        assert bank_accounts[1].iban == fake_iban
        assert bank_accounts[1].offerer == venue.managingOfferer
        assert bank_accounts[1].status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_accounts[1].label == "Intitulé du compte bancaire"
        assert bank_accounts[1].dsApplicationId == 123

        assert not offerers_models.VenueBankAccountLink.query.count()

        assert not history_models.ActionHistory.query.count()
        assert finance_models.BankAccountStatusHistory.query.count() == 2

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_association_to_physical_venue_if_both_virtual_and_physical_exists(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VirtualVenueFactory(managingOfferer=venue.managingOfferer)
        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "BICAGRIFRPP"
        assert bank_information.iban == "FR7630006000011234567890189"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        link = offerers_models.VenueBankAccountLink.query.one()
        assert link.venue == venue
        assert link.bankAccount == bank_account

        assert history_models.ActionHistory.query.count() == 1
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=True)
    def test_bank_information_are_updated_by_new_journey_accordingly_to_the_old_journey(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue_with_bank_information = offerers_factories.VenueFactory(
            pricing_point="self", managingOfferer__siren=siren
        )
        old_application_id = 8
        finance_factories.BankInformationFactory(
            applicationId=old_application_id,
            venue=venue_with_bank_information,
            status=finance_models.BankInformationStatus.DRAFT,
        )

        mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value
        )
        # We should erased the old bank information, and replace it with the new one
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        newly_bank_information = finance_models.BankInformation.query.one()
        assert newly_bank_information.venue == venue_with_bank_information
        assert newly_bank_information.applicationId != old_application_id
        assert newly_bank_information.bic == "BICAGRIFRPP"
        assert newly_bank_information.iban == "FR7630006000011234567890189"
        assert newly_bank_information.status == finance_models.BankInformationStatus.ACCEPTED
        assert newly_bank_information.venue == venue_with_bank_information

        # New journey
        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue_with_bank_information.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        link = offerers_models.VenueBankAccountLink.query.one()
        assert link.venue == venue_with_bank_information
        assert link.bankAccount == bank_account

        assert history_models.ActionHistory.query.count() == 1
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

    @override_features(WIP_ENABLE_DOUBLE_MODEL_WRITING=False)
    def test_dsv4_draft_application_is_handled_when_complete_after_new_journey_active(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.draft.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic is None
        assert bank_information.iban is None
        assert bank_information.status == finance_models.BankInformationStatus.DRAFT

        # New journey is not active, we shouldn't have any BankAccount
        assert not finance_models.BankAccount.query.all()

        # We need to invalidate the cache for the FF values, otherwise, the below code would still be executed
        # in a deactivated FF context
        del flask.request._cached_features
        # New journey is active, and the cron task is executed
        ff = Feature.query.filter(Feature.name == "WIP_ENABLE_DOUBLE_MODEL_WRITING").one()
        ff.isActive = True
        db_session.add(ff)
        db_session.commit()

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        # Old journey
        bank_information = finance_models.BankInformation.query.one()
        assert bank_information.venue == venue
        assert bank_information.bic == "SOGEFRPP"
        assert bank_information.iban == "FR7630007000111234567890144"
        assert bank_information.status == finance_models.BankInformationStatus.ACCEPTED

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_has_calls([call("Q2zzbXAtNzgyODAw"), call("Q2zzbXAtNzgyODAw")])

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0
