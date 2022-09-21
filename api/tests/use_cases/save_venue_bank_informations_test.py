from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors import sirene
from pcapi.connectors.dms.models import GraphQLApplicationStates
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
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
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, None, errors)
            assert errors.errors["Venue"] == ["Venue not found"]

        def test_raises_an_error_if_no_venue_found_by_dms_token(self):
            application_details = ApplicationDetail(
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                modification_date=datetime.utcnow(),
                dms_token="1234567890abcdef",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, None, errors)
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
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, None, errors)
            assert errors.errors["Venue"] == ["Error while checking SIRET on Sirene API"]

        def test_raises_an_error_if_no_venue_found_by_name(self):
            offerer = offerers_factories.OffererFactory()
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                venue_name="venuedemo",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, offerer, errors)
            assert errors.errors["Venue"] == ["Venue name not found"]

        def test_raises_an_error_if_more_than_one_venue_found(self):
            offerer = offerers_factories.OffererFactory()
            offerers_factories.VenueFactory.build_batch(
                2, managingOfferer=offerer, name="venuedemo", siret=None, comment="No siret"
            )
            application_details = ApplicationDetail(
                siren="999999999",
                status=BankInformationStatus.ACCEPTED,
                application_id=1,
                iban="XXX",
                bic="YYY",
                modification_date=datetime.utcnow(),
                venue_name="venuedemo",
            )
            errors = ApiErrors()

            self.save_venue_bank_informations.get_referent_venue(application_details, offerer, errors)
            assert errors.errors["Venue"] == ["Multiple venues found"]

    class SaveBankInformationTest:
        @patch("pcapi.connectors.dms.api.get_application_details")
        @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
        class VenueWithSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    venue_repository=VenueWithBasicInformationSQLRepository(),
                    bank_informations_repository=BankInformationsSQLRepository(),
                )

            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="refused",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                        updated_at="2020-01-01T10:10:10.10Z",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED
                assert bank_information.dateModified == datetime(2020, 1, 1, 10, 10, 10, 100000)

            def test_when_dms_state_is_received_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            @patch("pcapi.connectors.sirene.siret_is_active", lambda siret: False)
            def test_when_siret_is_not_active_should_not_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                assert BankInformation.query.count() == 0

            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    businessUnit=None,
                    siret="79387503012345",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            def test_when_no_offerer_is_found_and_status_is_closed_should_raise_and_not_create_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerers_factories.VenueFactory(
                    siret="79387503012345", managingOfferer__siren="123456789", businessUnit=None
                )
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                assert error.value.errors == {"Offerer": ["Offerer not found"]}
                assert BankInformation.query.count() == 0

            def test_when_no_offerer_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                assert BankInformation.query.count() == 0

            def test_when_no_venue_is_found_and_status_is_closed_should_raise_and_not_create_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                offerers_factories.OffererFactory(siren="793875030")
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                assert error.value.errors == {"Venue": ["Venue not found"]}
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

            def test_when_no_venue_is_found_but_status_is_not_closed_should_not_create_bank_information_and_not_raise(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                offerers_factories.OffererFactory(siren="793875030")
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                assert BankInformation.query.count() == 0

        @patch("pcapi.connectors.dms.api.get_application_details")
        @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
        class VenueWitoutSiretTest:
            def setup_method(self):
                self.save_venue_bank_informations = SaveVenueBankInformations(
                    venue_repository=VenueWithBasicInformationSQLRepository(),
                    bank_informations_repository=BankInformationsSQLRepository(),
                )

            def test_when_dms_state_is_refused_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=None,
                    comment="no siret",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="refused",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            def test_when_dms_state_is_without_continuation_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=None,
                    comment="no siret",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="without_continuation",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.REJECTED

            def test_when_dms_state_is_closed_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=None,
                    comment="no siret",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic == "SOGEFRPP"
                assert bank_information.iban == "FR7630007000111234567890144"
                assert bank_information.status == BankInformationStatus.ACCEPTED

            def test_when_dms_state_is_received_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=None,
                    comment="no siret",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            def test_when_dms_state_is_initiated_should_create_the_correct_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                venue = offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=None,
                    comment="no siret",
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information = BankInformation.query.one()
                assert bank_information.venue == venue
                assert bank_information.bic is None
                assert bank_information.iban is None
                assert bank_information.status == BankInformationStatus.DRAFT

            def test_when_no_offerer_is_found_but_status_is_not_closed_should_not_raise(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="initiated",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                assert BankInformation.query.count() == 0

            def test_when_no_offerer_is_found_and_state_is_closed_should_raise_and_not_create_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                assert error.value.errors == {"Offerer": ["Offerer not found"]}
                assert BankInformation.query.count() == 0

            def test_when_no_venue_without_siret_is_found_and_state_is_closed_should_raise_and_not_create_bank_information(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                offerers_factories.VenueFactory(
                    name="VENUE_NAME",  # used in DMS response fixture
                    businessUnit=None,
                    siret=79387503012345,
                    managingOfferer__siren="793875030",
                )
                application_id = "8"
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="closed",
                    )
                )

                # When
                with pytest.raises(CannotRegisterBankInformation) as error:
                    self.save_venue_bank_informations.execute(application_id)

                # Then
                assert error.value.errors["Venue"] == ["Venue name not found"]
                assert BankInformation.query.count() == 0

            def test_when_no_venue_is_found_but_status_is_not_closed_should_not_raise(
                self, mock_archive_dossier, mock_application_details, app
            ):
                # Given
                application_id = "8"
                offerers_factories.OffererFactory(siren="793875030")
                mock_application_details.return_value = (
                    dms_creators.venue_demarche_simplifiee_application_detail_response_without_siret(
                        siret="79387503012345",
                        bic="SOGEFRPP",
                        iban="FR7630007000111234567890144",
                        idx=int(application_id),
                        state="received",
                    )
                )

                # When
                self.save_venue_bank_informations.execute(application_id)

                # Then
                bank_information_count = BankInformation.query.count()
                assert bank_information_count == 0

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient")
    class SaveBankInformationV4ProcedureTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_draft_application(self, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bic.return_value = (
                dms_creators.venue_application_detail_response_procedure_v4(
                    state=GraphQLApplicationStates.draft.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT

        def test_on_going_application(self, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bic.return_value = (
                dms_creators.venue_application_detail_response_procedure_v4(
                    state=GraphQLApplicationStates.on_going.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.DRAFT

        def test_accepted_application(self, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bic.return_value = (
                dms_creators.venue_application_detail_response_procedure_v4(
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

        def test_refused_application(self, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bic.return_value = (
                dms_creators.venue_application_detail_response_procedure_v4(
                    state=GraphQLApplicationStates.refused.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED

        def test_without_continuation_application(self, mock_dms_graphql_client, app):
            venue = offerers_factories.VenueFactory(businessUnit=None, pricing_point="self")
            application_id = "9"
            mock_dms_graphql_client.return_value.get_bic.return_value = (
                dms_creators.venue_application_detail_response_procedure_v4(
                    state=GraphQLApplicationStates.without_continuation.value, dms_token=venue.dmsToken
                )
            )

            self.save_venue_bank_informations.execute(application_id, procedure_id=settings.DMS_VENUE_PROCEDURE_ID_V4)

            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic is None
            assert bank_information.iban is None
            assert bank_information.status == BankInformationStatus.REJECTED

    @patch("pcapi.connectors.dms.api.get_application_details")
    @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
    class UpdateBankInformationByApplicationIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        def test_when_rib_and_offerer_change_everything_should_be_updated(
            self, mock_archive_dossier, mock_application_details, app
        ):
            # Given
            bank_information = finance_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=offerers_factories.VenueFactory(businessUnit=None),
            )
            new_venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="12345678912345",
                managingOfferer__siren="123456789",
            )
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="12345678912345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=bank_information.applicationId,
                )
            )

            # When
            self.save_venue_bank_informations.execute(str(bank_information.applicationId))

            # Then
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.offererId == None
            assert bank_information.venueId == new_venue.id

        def test_when_status_change_rib_should_be_correctly_updated(
            self, mock_archive_dossier, mock_application_details, app
        ):
            # Given
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            bank_information = finance_factories.BankInformationFactory(
                applicationId=8,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED,
            )
            application_id = "8"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="QSDFGH8Z555",
                    iban="NL36INGB2682297498",
                    idx=int(application_id),
                    state="initiated",
                )
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information = BankInformation.query.one()
            assert bank_information.venue == venue
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        def test_when_overriding_another_bank_information_should_raise(
            self, mock_archive_dossier, mock_application_details, app
        ):
            # Given
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
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387501912345",
                    bic="QSDFGH8Z555",
                    iban="NL36INGB2682297498",
                    idx=int(application_id),
                )
            )

            # When
            with pytest.raises(ApiErrors) as errors:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 2
            assert errors.value.errors['"venueId"'] == [
                "Une entrée avec cet identifiant existe déjà dans notre base de données"
            ]

    @patch("pcapi.connectors.dms.api.get_application_details")
    class UpdateBankInformationByVenueIdTest:
        def setup_method(self):
            self.save_venue_bank_informations = SaveVenueBankInformations(
                venue_repository=VenueWithBasicInformationSQLRepository(),
                bank_informations_repository=BankInformationsSQLRepository(),
            )

        @patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
        def test_when_receive_new_closed_application_should_override_previous_one(
            self, mock_archive_dossier, mock_application_details, app
        ):
            # Given
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            bank_information = finance_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                dateModified=datetime(2018, 1, 1),
            )
            application_id = "8"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=int(application_id),
                )
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "SOGEFRPP"
            assert bank_information.iban == "FR7630007000111234567890144"
            assert bank_information.applicationId == 8
            assert finance_models.BusinessUnit.query.count() == 1
            business_unit = finance_models.BusinessUnit.query.one()
            assert business_unit.bankAccountId == bank_information.id
            assert venue.businessUnitId == business_unit.id

        def test_when_receive_new_application_with_draft_state_should_update_previously_rejected_bank_information(
            self, mock_application_details, app
        ):
            # Given
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            application_id = "8"
            bank_information = finance_factories.BankInformationFactory(
                applicationId=79,
                bic=None,
                iban=None,
                venue=venue,
                status=BankInformationStatus.REJECTED,
            )
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=int(application_id),
                    state="initiated",
                )
            )

            # When
            self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            bank_information = BankInformation.query.one()
            assert bank_information.bic == None
            assert bank_information.iban == None
            assert bank_information.status == BankInformationStatus.DRAFT

        def test_when_receive_new_application_with_lower_status_should_reject(self, mock_application_details, app):
            # Given
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            bank_information = finance_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                status=BankInformationStatus.ACCEPTED,
            )
            application_id = "8"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=int(application_id),
                    state="initiated",
                )
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "QSDFGH8Z555"
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79
            assert error.value.errors == {
                "BankInformation": ["Received dossier is in draft state. Move it to 'Accepté' to save it."]
            }

        def test_when_receive_older_application_should_reject(self, mock_application_details, app):
            # Given
            venue = offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            bank_information = finance_factories.BankInformationFactory(
                applicationId=79,
                bic="QSDFGH8Z555",
                iban="NL36INGB2682297498",
                venue=venue,
                dateModified=datetime(2021, 1, 1),
            )
            application_id = "8"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=int(application_id),
                )
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            bank_information = BankInformation.query.one()
            assert bank_information.bic == "QSDFGH8Z555"
            assert bank_information.iban == "NL36INGB2682297498"
            assert bank_information.status == BankInformationStatus.ACCEPTED
            assert bank_information.applicationId == 79
            assert error.value.errors == {"BankInformation": ["Received application details are older than saved one"]}

        def test_when_state_is_unknown(self, mock_application_details, app):
            # Given
            offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            application_id = "8"
            unknown_status = "unknown_status"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOGEFRPP",
                    iban="FR7630007000111234567890144",
                    idx=int(application_id),
                    state=unknown_status,
                )
            )

            # When
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            # Then
            assert error.value.errors == {"BankInformation": f"Unknown Demarches Simplifiées state {unknown_status}"}
            assert BankInformation.query.count() == 0

        def test_raises_an_error_when_bank_information_data_is_invalid(self, mock_application_details, app):
            offerers_factories.VenueFactory(
                businessUnit=None,
                siret="79387503012345",
                managingOfferer__siren="793875030",
            )
            application_id = "8"
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="SOG",
                    iban="FR76",
                    idx=int(application_id),
                )
            )
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            assert error.value.errors == {
                "bic": ['Le BIC renseigné ("SOG") est invalide'],
                "iban": ['L’IBAN renseigné ("FR76") est invalide'],
            }
            assert BankInformation.query.count() == 0

        def test_raises_an_error_when_no_bank_information_data_is_provided(self, mock_application_details, app):
            application_id = "8"
            offerer = offerers_factories.OffererFactory(siren="793875030")
            offerers_factories.VenueFactory(managingOfferer=offerer, siret="79387503012345", businessUnit=None)
            mock_application_details.return_value = (
                dms_creators.venue_demarche_simplifiee_application_detail_response_with_siret(
                    siret="79387503012345",
                    bic="",
                    iban="",
                    idx=int(application_id),
                )
            )
            with pytest.raises(CannotRegisterBankInformation) as error:
                self.save_venue_bank_informations.execute(application_id)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 0
            assert error.value.errors == {
                "bic": ["Cette information est obligatoire"],
                "iban": ["Cette information est obligatoire"],
            }

    @patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
    @patch(
        "pcapi.use_cases.save_venue_bank_informations.get_venue_bank_information_application_details_by_application_id"
    )
    class SaveBankInformationUpdateTextOnErrorTest:
        application_id = 1
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
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetail(**application_data)

        def test_update_text_offerer_not_found(self, mock_application_details, mock_update_text_annotation, app):
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Offerer: Offerer not found"
            )

        def test_update_text_offerer_not_found_for_draft(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.DRAFT}
            )

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Offerer: Offerer not found"
            )

        def test_update_text_offerer_not_found_for_rejected(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.REJECTED}
            )

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_not_called()

        def test_update_text_venue_not_found(self, mock_application_details, mock_update_text_annotation, app):
            offerers_factories.OffererFactory(siren="999999999")
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Venue: Venue name not found"
            )

        def test_update_text_venue_multiple_found(self, mock_application_details, mock_update_text_annotation, app):
            offerer = offerers_factories.OffererFactory(siren="999999999")
            offerers_factories.VenueFactory.build_batch(
                2, name="venuedemo", managingOfferer=offerer, siret=None, comment="No siret", businessUnit=None
            )
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Venue: Multiple venues found"
            )

        def test_update_text_no_venue_with_same_siret_found(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            mock_application_details.return_value = self.build_application_detail({"siret": "36252187900034"})

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id, self.annotation_id, "Venue: Venue not found"
            )

        def test_update_text_application_details_older_than_saved(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034")
            finance_factories.BankInformationFactory(dateModified=datetime.utcnow(), venue=venue)
            yesterday = datetime.utcnow() - timedelta(days=1)
            mock_application_details.return_value = self.build_application_detail(
                {"siret": "36252187900034", "modification_date": yesterday}
            )

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received application details are older than saved one",
            )

        def test_update_text_application_details_has_more_advanced_status(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034")
            finance_factories.BankInformationFactory(venue=venue, status=BankInformationStatus.ACCEPTED)
            mock_application_details.return_value = self.build_application_detail(
                {"siret": "36252187900034", "status": BankInformationStatus.DRAFT}
            )

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received dossier is in draft state. Move it to 'Accepté' to save it.",
            )

        def test_update_text_application_details_is_rejected_status(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            venue = offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034")
            finance_factories.BankInformationFactory(venue=venue, status=BankInformationStatus.ACCEPTED)
            mock_application_details.return_value = self.build_application_detail(
                {"siret": "36252187900034", "status": BankInformationStatus.REJECTED}
            )

            self.save_venue_bank_informations.execute(self.application_id)

            mock_update_text_annotation.assert_called_once_with(
                self.dossier_id,
                self.annotation_id,
                "BankInformation: Received application details state does not allow to change bank information",
            )

        def test_update_text_application_details_on_bank_information_error(
            self, mock_application_details, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034")
            mock_application_details.return_value = self.build_application_detail(
                {"siret": "36252187900034", "bic": "", "iban": "INVALID"}
            )

            self.save_venue_bank_informations.execute(self.application_id)

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
            }
            if updated_field:
                application_data.update(updated_field)
            return ApplicationDetail(**application_data)

        def test_update_text_annotation_and_archive_on_validated_bank_information(
            self, mock_application_details, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034", businessUnit=None)
            mock_application_details.return_value = self.build_application_detail()

            self.save_venue_bank_informations.execute(1)

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
            offerers_factories.OffererFactory(siren="999999999")
            offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034", businessUnit=None)
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.REJECTED}
            )
            self.save_venue_bank_informations.execute(1)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            mock_archive_dossier.asserrt_called_once_with("DOSSIER_ID")

        def test_update_text_application_details_on_draft_bank_information(
            self, mock_application_details, mock_archive_dossier, mock_update_text_annotation, app
        ):
            offerers_factories.OffererFactory(siren="999999999")
            offerers_factories.VenueFactory(name="venuedemo", siret="36252187900034", businessUnit=None)
            mock_application_details.return_value = self.build_application_detail(
                {"status": BankInformationStatus.DRAFT}
            )

            self.save_venue_bank_informations.execute(1)

            bank_information_count = BankInformation.query.count()
            assert bank_information_count == 1
            mock_update_text_annotation.assert_called_once_with(
                "DOSSIER_ID",
                "ANNOTATION_ID",
                "Valid dossier",
            )
            mock_archive_dossier.assert_not_called()
