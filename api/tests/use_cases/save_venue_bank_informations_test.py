from base64 import b64encode
from datetime import datetime
from unittest.mock import patch

import pytest
import schwifty

from pcapi import settings
from pcapi.connectors.dms.models import GraphQLApplicationStates
from pcapi.core.finance import models as finance_models
from pcapi.core.finance.ds import update_ds_applications_for_procedure
import pcapi.core.finance.factories as finance_factories
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.offers import factories as offers_factories

import tests.connector_creators.demarches_simplifiees_creators as dms_creators


pytestmark = pytest.mark.usefixtures("db_session")


@patch("pcapi.connectors.dms.api.DMSGraphQLClient.execute_query")
@patch("pcapi.use_cases.save_venue_bank_informations.update_demarches_simplifiees_text_annotations")
@patch("pcapi.use_cases.save_venue_bank_informations.archive_dossier")
class BankAccountJourneyTest:
    dsv4_application_id = 9
    dsv5_application_id = 14742654
    b64_encoded_application_id = "RG9zc2llci0xNDc0MjY1NA=="
    error_annotation_id = "Q2hhbXAtMzYzMDA5NQ=="

    def test_DSv4_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0

    def test_edge_case_label_too_long_format_DSv4(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(
            pricing_point="self",
            managingOfferer__siren=siren,
            publicName="The longest name ever PARIS LIBRAIRIES ASSOCIATION DES LIBRAIRIES DE PARIS LIBRAIRIE COMME UN ROMAN 39 RUE DE BRETAGNE 75003 PARIS",
        )
        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)
        bank_account = finance_models.BankAccount.query.one()
        assert len(bank_account.label) <= 100
        assert bank_account.label[-3:] == "..."  # Check the placeholder indication

    def test_v4_stop_using_bank_informations_and_bank_account_if_rejected(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v4_as_batch(
            state=GraphQLApplicationStates.accepted.value, dms_token=venue.dmsToken
        )
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

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
        update_ds_applications_for_procedure(settings.DMS_VENUE_PROCEDURE_ID_V4, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.status == finance_models.BankAccountApplicationStatus.REFUSED
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue
        assert bank_account_link.bankAccount == bank_account
        assert bank_account_link.timespan.upper is not None

    def test_v5_stop_using_bank_informations_and_bank_account_if_rejected(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

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
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.status == finance_models.BankAccountApplicationStatus.REFUSED

        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue
        assert bank_account_link.bankAccount == bank_account
        assert bank_account_link.timespan.upper is not None

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

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.common_name
        assert bank_account.dsApplicationId == self.dsv4_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == venue_with_no_bank_account.bookingEmail

    def test_creating_DSv4_with_already_existing_link_should_deprecate_old_one_and_create_new_one(
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

        mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

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

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "SOGEFRPP"
        assert bank_account.iban == "FR7630007000111234567890144"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == venue.name
        mock_archive_dossier.assert_called_once_with("Q2zzbXAtNzgyODAw")

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

    def test_DSv5_is_handled(self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerer = venue.managingOfferer

        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == offerer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        bank_account_link = offerers_models.VenueBankAccountLink.query.one()
        assert bank_account_link.venue == venue

        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

        assert history_models.ActionHistory.query.count() == 1  # One link created
        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

        assert len(mails_testing.outbox) == 0

    def test_edge_case_label_too_long_format_DSv5(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client
    ):
        siret = "85331845900049"
        siren = siret[:9]
        offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.accepted.value,
            label="PARIS LIBRAIRIES ASSOCIATION DES LIBRAIRIES DE PARIS LIBRAIRIE COMME UN ROMAN 39 RUE DE BRETAGNE 75003 PARIS",
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)
        bank_account = finance_models.BankAccount.query.one()
        assert len(bank_account.label) <= 100
        assert bank_account.label[-3:] == "..."  # Check the placeholder indication

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

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ACCEPTED
        assert bank_account.label == "Intitulé du compte bancaire"
        mock_archive_dossier.assert_called_once_with("RG9zc2llci0xNDc0MjY1NA==")

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

    def test_DSv5_pending_correction_status_handled(
        self, mock_archive_dossier, mock_update_text_annotation, mock_graph_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)

        mock_graph_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.draft.value, last_pending_correction_date="2023-10-27T14:51:09+02:00"
        )

        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.WITH_PENDING_CORRECTIONS
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id
        mock_archive_dossier.assert_not_called()

        assert not offerers_models.VenueBankAccountLink.query.count()
        assert not history_models.ActionHistory.query.count()

        on_going_status_history = finance_models.BankAccountStatusHistory.query.one()

        assert on_going_status_history.status == bank_account.status
        assert not on_going_status_history.timespan.upper

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

    def test_legacy_data_convert_into_bank_account_does_not_have_status_history(
        self, mock_archive_dossier, mock_update_text_annotation, mock_grapqhl_client, db_session
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        # Legacy bankInformation turned into a bankAccount
        finance_factories.BankAccountFactory(
            iban="FR7630006000011234567890189",
            bic="BICAGRIFRPP",
            offerer=venue.managingOfferer,
            status=finance_models.BankAccountApplicationStatus.DRAFT,
            label="Intitulé du compte bancaire",
            dsApplicationId=self.dsv5_application_id,
        )

        # The DS application status change, this should work, even if the bankAccount doesn't have a BankAccountStatusHistory
        mock_grapqhl_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
            state=GraphQLApplicationStates.on_going.value,
        )
        update_ds_applications_for_procedure(settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        bank_account = finance_models.BankAccount.query.one()
        assert bank_account.bic == "BICAGRIFRPP"
        assert bank_account.iban == "FR7630006000011234567890189"
        assert bank_account.offerer == venue.managingOfferer
        assert bank_account.status == finance_models.BankAccountApplicationStatus.ON_GOING
        assert bank_account.label == "Intitulé du compte bancaire"
        assert bank_account.dsApplicationId == self.dsv5_application_id

        assert finance_models.BankAccountStatusHistory.query.count() == 1  # One status change recorded

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

    @pytest.mark.parametrize(
        "fake_iban,fake_bic",
        [
            ("XR7630006000011234567890189", None),
            (None, "FAKEBICIFRPX"),
        ],
    )
    def test_validation_on_iban_and_bic(
        self, mock_archive_dossier, mock_update_text_annotation, mock_dms_graphql_client, fake_iban, fake_bic
    ):
        siret = "85331845900049"
        siren = siret[:9]
        venue = offerers_factories.VenueFactory(pricing_point="self", managingOfferer__siren=siren)
        offerers_factories.VirtualVenueFactory(managingOfferer=venue.managingOfferer)

        if fake_iban:
            mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
                state=GraphQLApplicationStates.draft.value, iban=fake_iban
            )
        elif fake_bic:
            mock_dms_graphql_client.return_value = dms_creators.get_bank_info_response_procedure_v5(
                state=GraphQLApplicationStates.draft.value, bic=fake_bic
            )

        update_ds_applications_for_procedure(procedure_number=settings.DS_BANK_ACCOUNT_PROCEDURE_ID, since=None)

        assert not finance_models.BankAccount.query.all()
        message = ""
        if fake_iban:
            message = "L'IBAN n'est pas valide"
        elif fake_bic:
            message = "Le BIC n'est pas valide"
        mock_update_text_annotation.assert_any_call(
            dossier_id=self.b64_encoded_application_id, annotation_id=self.error_annotation_id, message=message
        )
