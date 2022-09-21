from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.connectors.dms.models import GraphQLApplicationStates
import pcapi.core.finance.factories as finance_factories
from pcapi.core.finance.models import BankInformation
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
from pcapi.domain.bank_information import CannotRegisterBankInformation
from pcapi.domain.demarches_simplifiees import ApplicationDetail
from pcapi.infrastructure.repository.bank_informations.bank_informations_sql_repository import (
    BankInformationsSQLRepository,
)
from pcapi.infrastructure.repository.venue.venue_with_basic_information.venue_with_basic_information_sql_repository import (
    VenueWithBasicInformationSQLRepository,
)
from pcapi.models.api_errors import ApiErrors
from pcapi.use_cases.save_venue_bank_informations import SaveVenueBankInformations

import tests.connector_creators.demarches_simplifiees_creators as dms_creators


pytestmark = pytest.mark.usefixtures("db_session")


class SaveVenueBankInformationsTest:
    class GetReferentVenueTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_raises_an_error_if_no_venue_found_by_siret(self):
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                siret="99999999900000",
            )
            errors = CannotRegisterBankInformation()

            self.save_venue_bank_informations.get_referent_venue(application_details, errors)
            assert errors.errors["Venue"] == ["Venue not found"]

        def test_raises_an_error_if_no_venue_found_by_dms_token(self):
            application_details = ApplicationDetail(
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                modification_date=datetime.utcnow(),
                dms_token="1234567890abcdef",
            )
            errors = CannotRegisterBankInformation()

            self.save_venue_bank_informations.get_referent_venue(application_details, errors)
            assert errors.errors["Venue"] == ["Venue not found"]

        @patch("pcapi.connectors.sirene.siret_is_active", side_effect=sirene.UnknownEntityException())
        def test_raises_an_error_if_sirene_api_errored(self, siret_is_active):
            offerer = offerers_factories.OffererFactory()
            offerers_factories.VenueFactory(managingOfferer=offerer, siret="99999999900000")
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                siret="99999999900000",
            )
            errors = CannotRegisterBankInformation()

            self.save_venue_bank_informations.get_referent_venue(application_details, errors)
            assert errors.errors["Venue"] == ["Error while checking SIRET on Sirene API"]

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class SaveBankInformationV4ProcedureTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_draft_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.draft.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_on_going_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.on_going.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_accepted_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert venue.current_reimbursement_point_id == venue.id
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_refused_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.refused.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_without_continuation_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.without_continuation.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class UpdateBankInformationV4ProcedureTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_update_bank_info_with_new_iban_bic(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue_with_accpeted_bank_info = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            bank_information = finance_factories.BankInformationFactory(
                applicationId=8,
                bic="SCROOGEBANK",
                iban="FR8888888888888888888888888",
                venue=venue_with_accpeted_bank_info,
            )
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(dms_token=venue_with_accpeted_bank_info.dmsToken)
            )

            self.save_venue_bank_informations.execute(
                str(bank_information.applicationId), procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.offererId == None
            assert bank_information.venueId == venue_with_accpeted_bank_info.id
            mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        def test_update_bank_info_with_draft_application(self, mock_archive_dossier, mock_dms_graphql_client, app):
            venue_with_accpeted_bank_info = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            finance_factories.BankInformationFactory(
                bic="SCROOGEBANK",
                iban="FR8888888888888888888888888",
                venue=venue_with_accpeted_bank_info,
                status=BankInformationStatus.DRAFT,
            )
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = (
                dms_creators.get_bank_info_response_procedure_v4(
                    state=GraphQLApplicationStates.on_going.value, dms_token=venue_with_accpeted_bank_info.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue_with_accpeted_bank_info
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT
            mock_archive_dossier.assert_not_called()

        def test_when_overriding_another_bank_information_should_raise(
            self, mock_archive_dossier, mock_dms_graphql_client, app
        ):
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
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
                businessUnit=None,
                siret="79387501912345",
                managingOfferer__siren="793875019",
            )
            finance_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=other_venue,
            )
            application_id = "8"
            duplicate_bank_info_return = dms_creators.get_bank_info_response_procedure_v4(
                dms_token=other_venue.dmsToken
            )
            duplicate_bank_info_return["dossier"]["champs"][3]["value"] = "NL36INGB2682297498"
            mock_dms_graphql_client.return_value.get_bank_info.return_value = duplicate_bank_info_return

            # When
            with pytest.raises(ApiErrors) as errors:
                self.save_venue_bank_informations.execute(
                    application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
                )

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 2
            assert errors.value.errors['"venueId"'] == [
                "Une entrée avec cet identifiant existe déjà dans notre base de données"
            ]
            mock_archive_dossier.assert_not_called()

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch(
        "pcapi.use_cases.save_venue_bank_informations.get_venue_bank_information_application_details_by_application_id"
    )
    class SaveBankInformationUpdateTextOnErrorTest:
        application_id = "1"
        annotation_id = "Q4hhaXAtOEE1NSg5"
        dossier_id = "Q4zzaXAtOEE1NSg5"

        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def build_application_detail(self, updated_field=None):
            application_data = {
                "siren": "999999999",
                "status": BankInformationStatus.ACCEPTED,
                "application_id": self.application_id,
                "iban": "FR7630007000111234567890144",
                "bic": "SOGEFRPP",
                "modification_date": datetime.utcnow(),
                "venue_name": "venuedemo",
                "error_annotation_id": self.annotation_id,
                "dossier_id": self.dossier_id,
                "dms_token": "1234567890abcdef",
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetail(**application_data)

        def test_update_text_venue_not_found(self, mock_application_details, mock_update_text_annotation, app):
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(
                self.application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Venue: Venue not found"
            )

        def test_update_text_application_details_older_than_saved(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(dateModified=datetime.utcnow(), venue=venue)
            yesterday = datetime.utcnow() - timedelta(days=1)
            mock_application_details.return_value = self.build_application_detail(
                {"dms_token": venue.dmsToken, "modification_date": yesterday}
            )

            self.save_venue_bank_informations.execute(
                self.application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received application details are older than saved one",
            )

        def test_update_text_application_details_has_more_advanced_status(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(venue=venue, status=BankInformationStatus.ACCEPTED)
            mock_application_details.return_value = self.build_application_detail(
                {"dms_token": venue.dmsToken, "status": BankInformationStatus.DRAFT}
            )

            self.save_venue_bank_informations.execute(
                self.application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received dossier is in draft state. Move it to 'Accepté' to save it.",
            )

        def test_update_text_application_details_is_rejected_status(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo")
            finance_factories.BankInformationFactory(venue=venue, status=BankInformationStatus.ACCEPTED)
            mock_application_details.return_value = self.build_application_detail(
                {"dms_token": venue.dmsToken, "status": BankInformationStatus.REJECTED}
            )

            self.save_venue_bank_informations.execute(
                self.application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received application details state does not allow to change bank information",
            )

        def test_update_text_application_details_on_bank_information_error(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            venue = offerers_factories.VenueFactory(name="venuedemo")
            mock_application_details.return_value = self.build_application_detail(
                {"dms_token": venue.dmsToken, "bic": "", "iban": "INVALID"}
            )

            self.save_venue_bank_informations.execute(
                self.application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4
            )

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                'iban: L’IBAN renseigné ("INVALID") est invalide; bic: Cette information est obligatoire',
            )

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    @patch(
        "pcapi.use_cases.save_venue_bank_informations.get_venue_bank_information_application_details_by_application_id"
    )
    class SaveBankInformationUpdateTextTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def build_application_detail(self, updated_field=None):
            application_data = {
                "siren": "999999999",
                "siret": "36252187900034",
                "status": BankInformationStatus.ACCEPTED,
                "application_id": 1,
                "iban": "FR7630007000111234567890144",
                "bic": "SOGEFRPP",
                "modification_date": datetime.utcnow(),
                "venue_name": "venuedemo",
                "error_annotation_id": "ANNOTATION_ID",
                "dossier_id": "DOSSIER_ID",
                "dms_token": "1234567890abcdef",
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetail(**application_data)

        def test_update_text_annotation_and_archive_on_validated_bank_information(
            self, mock_application_details, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(
                name="venuedemo", businessUnit=None, pricing_point="self", dmsToken="1234567890abcdef"
            )
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(1, settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            mock_update_text_annotation.assert_called_once_with(
                "DOSSIER_ID",
                "ANNOTATION_ID",
                "Dossier successfully imported",
            )
            mock_archive_dossier.asserrt_called_once_with("DOSSIER_ID")

        def test_archive_dossier_on_refused_bank_information(
            self, mock_application_details, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(name="venuedemo", businessUnit=None, dmsToken="1234567890abcdef")
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.REJECTED}
            )
            self.save_venue_bank_informations.execute(1, settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            mock_archive_dossier.asserrt_called_once_with("DOSSIER_ID")

        def test_update_text_application_details_on_draft_bank_information(
            self, mock_application_details, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.VenueFactory(name="venuedemo", businessUnit=None, dmsToken="1234567890abcdef")
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.DRAFT}
            )

            self.save_venue_bank_informations.execute(1, settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            mock_update_text_annotation.assert_called_once_with(
                "DOSSIER_ID",
                "ANNOTATION_ID",
                "Valid dossier",
            )
            mock_archive_dossier.assert_not_called()
