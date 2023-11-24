from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.connectors.dms.serializer import ApplicationDetailOldJourney
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.ds import update_ds_applications_for_procedure
import pcapi.core.finance.factories as finance_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.domain.demarches_simplifiees import parse_raw_bank_info_data
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.models.api_errors import ApiErrors
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformationsFactory
from pcapi.utils.urls import build_pc_pro_venue_link

import tests.connector_creators.demarches_simplifiees_creators as dms_creators


pytestmark = pytest.mark.usefixtures("db_session")


class SaveVenueBankInformationsTest:
    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    class GetReferentVenueTest:
        def setup_method(self):
            SaveVenueBankInformationsV3 = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V3)
            SaveVenueBankInformationsV4 = SaveVenueBankInformationsFactory.get(settings.DMS_VENUE_PROCEDURE_ID_V4)
            self.save_venue_bank_informations_v3 = SaveVenueBankInformationsV3(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )
            self.save_venue_bank_informations_v4 = SaveVenueBankInformationsV4(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_v3_raises_an_error_if_siret_is_absent(self, mock_update_text_annotation):
            application_details = ApplicationDetailOldJourney(
                application_type=3,
                siren="999999999",
                status=GraphQLApplicationStates.accepted.value,
                application_id=1,
                dossier_id="2",
                iban="XXX",
                bic="YYY",
                updated_at=datetime.utcnow().isoformat(),
                siret=None,
                error_annotation_id="Q2hhbXAtMTIzNDUK",
                venue_url_annotation_id=None,
            )

            self.save_venue_bank_informations_v3.get_referent_venue(
                application_details,
            )
            assert self.save_venue_bank_informations_v3.api_errors.errors["Venue"] == ["Venue not found"]

        def test_v3_raises_an_error_if_no_venue_found_by_siret(self, mock_update_text_annotation):
            application_details = ApplicationDetailOldJourney(
                application_type=3,
                siren="999999999",
                status=GraphQLApplicationStates.accepted.value,
                application_id=1,
                dossier_id="2",
                iban="XXX",
                bic="YYY",
                updated_at=datetime.utcnow().isoformat(),
                siret="99999999900000",
                error_annotation_id="Q2hhbXAtMTIzNDUK",
                venue_url_annotation_id=None,
            )

            self.save_venue_bank_informations_v3.get_referent_venue(
                application_details,
            )
            assert self.save_venue_bank_informations_v3.api_errors.errors["Venue"] == ["Venue not found"]

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

        @patch("pcapi.connectors.sirene.siret_is_active", side_effect=sirene.UnknownEntityException())
        def test_v3_raises_an_error_if_sirene_api_errored(self, siret_is_active, mock_update_text_annotation):
            offerer = offerers_factories.OffererFactory()
            offerers_factories.VenueFactory(managingOfferer=offerer, siret="99999999900000")
            application_details = ApplicationDetailOldJourney(
                application_type=3,
                siren="999999999",
                status=GraphQLApplicationStates.accepted.value,
                application_id=1,
                dossier_id="2",
                iban="XXX",
                bic="YYY",
                updated_at=datetime.utcnow().isoformat(),
                siret="99999999900000",
                error_annotation_id="Q2hhbXAtMTIzNDUK",
                venue_url_annotation_id=None,
            )

            self.save_venue_bank_informations_v3.get_referent_venue(
                application_details,
            )
            assert self.save_venue_bank_informations_v3.api_errors.errors["Venue"] == [
                "Error while checking SIRET on Sirene API"
            ]

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
            mock_archive_dossier.asserrt_called_once_with("DOSSIER_ID")

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
            mock_archive_dossier.asserrt_called_once_with("DOSSIER_ID")

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

    def test_dont_write_annotations_if_any_exists(
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
        mock_update_text_annotation.assert_called_once_with(
            self.b64_encoded_application_id, "Q2hhbXAtMjc1NzMyOQ==", build_pc_pro_venue_link(venue)
        )
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
