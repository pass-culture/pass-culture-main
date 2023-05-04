import datetime
import decimal
import os
import pathlib
import time
from unittest.mock import patch

from freezegun import freeze_time
import jwt
import pytest
import sqlalchemy as sa

from pcapi.connectors import sirene
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.exceptions as offerers_exceptions
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.providers import factories as providers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.models import api_errors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization import base as serialize_base
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.human_ids import humanize

import tests
from tests.test_utils import gen_offerer_tags


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("ape_code, expected_tag", list(offerers_api.APE_TAG_MAPPING.items()))
def test_new_offerer_auto_tagging(db_session, ape_code, expected_tag):
    # given
    gen_offerer_tags()
    offerer = offerers_factories.OffererFactory()
    siren_info = sirene.SirenInfo(
        ape_code=ape_code,
        siren="777123456",
        name="this is not a name",
        head_office_siret="77712345600000",
        legal_category_code="don't know",
    )
    user = users_factories.UserFactory()

    # when
    offerers_api.auto_tag_new_offerer(offerer, siren_info, user)

    # then
    db_session.refresh(offerer)
    assert expected_tag in (tag.label for tag in offerer.tags)


class CreateVenueTest:
    def base_data(self, offerer):
        return {
            "address": "rue du test",
            "city": "Paris",
            "postalCode": "75000",
            "latitude": 1,
            "longitude": 1,
            "managingOffererId": offerer.id,
            "name": "La Venue",
            "venueTypeCode": "VISUAL_ARTS",
            "bookingEmail": "venue@example.com",
            "siret": offerer.siren + "00000",
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }

    def test_basics(self):
        offerer = offerers_factories.OffererFactory()
        data = venues_serialize.PostVenueBodyModel(**self.base_data(offerer))
        offerers_api.create_venue(data)

        venue = offerers_models.Venue.query.one()
        assert venue.address == "rue du test"
        assert venue.city == "Paris"
        assert venue.postalCode == "75000"
        assert venue.latitude == 1
        assert venue.longitude == 1
        assert venue.managingOfferer == offerer
        assert venue.name == "La Venue"
        assert venue.bookingEmail == "venue@example.com"
        assert venue.dmsToken
        assert venue.current_pricing_point_id == venue.id

    def test_venue_with_no_siret_has_no_pricing_point(self):
        offerer = offerers_factories.OffererFactory()
        data = self.base_data(offerer) | {"siret": None, "comment": "no siret"}
        data = venues_serialize.PostVenueBodyModel(**data)

        offerers_api.create_venue(data)

        venue = offerers_models.Venue.query.one()
        assert venue.siret is None
        assert venue.current_pricing_point_id is None


class EditVenueTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_name_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"name": "my new name"}
        offerers_api.update_venue(venue, author=user, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_public_name_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"publicName": "my new name"}
        offerers_api.update_venue(venue, author=user, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_city_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "My new city"}
        offerers_api.update_venue(venue, author=user, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_are_not_on_algolia_fields_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids
    ):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
            bookingEmail="old@email.com",
        )

        # When
        json_data = {"bookingEmail": "new@email.com"}
        offerers_api.update_venue(venue, author=user, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_in_payload_are_same_as_previous_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids
    ):
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "old City"}
        offerers_api.update_venue(venue, author=user, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    def test_empty_siret_is_editable(self, app) -> None:
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueWithoutSiretFactory()

        venue_data = {
            "siret": venue.managingOfferer.siren + "11111",
        }

        # when
        updated_venue = offerers_api.update_venue(venue, author=user, **venue_data)

        # Then
        assert updated_venue.siret == venue_data["siret"]

    def test_existing_siret_is_not_editable(self, app) -> None:
        # Given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()

        # when
        venue_data = {
            "siret": venue.managingOfferer.siren + "54321",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, author=user, **venue_data)

        # Then
        assert error.value.errors["siret"] == ["Vous ne pouvez pas modifier le siret d'un lieu"]

    def test_latitude_and_longitude_wrong_format(self, app) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            isVirtual=False,
        )

        # when
        venue_data = {
            "latitude": -98.82387,
            "longitude": "112°3534",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, author=user, **venue_data)

        # Then
        assert error.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
        assert error.value.errors["longitude"] == ["Format incorrect"]

    def test_accessibility_fields_are_updated(self, app) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()

        # when
        venue_data = {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }

        offerers_api.update_venue(venue, author=user, **venue_data)

        venue = offerers_models.Venue.query.get(venue.id)
        assert venue.audioDisabilityCompliant
        assert venue.mentalDisabilityCompliant
        assert venue.motorDisabilityCompliant is False
        assert venue.visualDisabilityCompliant is False

    def test_no_modifications(self, app) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()

        # when
        venue_data = {
            "departementCode": venue.departementCode,
            "city": venue.city,
            "motorDisabilityCompliant": venue.motorDisabilityCompliant,
        }
        contact_data = serialize_base.VenueContactModel(
            email=venue.contact.email,
            phone_number=venue.contact.phone_number,
            social_medias=venue.contact.social_medias,
            website=venue.contact.website,
        )

        # nothing has changed => nothing to save nor update
        with assert_num_queries(0):
            offerers_api.update_venue(venue, contact_data=contact_data, author=user, **venue_data)

    def test_update_only_venue_contact(self, app):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        contact_data = serialize_base.VenueContactModel(email="other.contact@venue.com", phone_number="0788888888")

        offerers_api.update_venue(venue, contact_data=contact_data, author=user_offerer.user)

        venue = offerers_models.Venue.query.get(venue.id)
        assert venue.contact
        assert venue.contact.phone_number == contact_data.phone_number
        assert venue.contact.email == contact_data.email

    def test_cannot_update_virtual_venue_name(self):
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory(siren="000000000")
        virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        venue_data = {"name": "Toto"}
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(virtual_venue, author=user, **venue_data)

        msg = "Vous ne pouvez modifier que le point de remboursement du lieu Offre Numérique."
        assert error.value.errors == {"venue": [msg]}

    def test_edit_venue_with_pending_bank_info(self):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(
            pricing_point="self", reimbursement_point="self", publicName="Nom actuel"
        )
        finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.DRAFT)
        venue_data = {
            "publicName": "Nouveau nom",
            "reimbursementPointId": venue.current_reimbursement_point_id,
            # all the other venue attributes should be in this dict
        }
        offerers_api.update_venue(venue, author=user, **venue_data)

        assert venue.publicName == "Nouveau nom"

    def test_no_venue_contact_no_modification(self, app) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(contact=None)

        # when
        venue_data = {
            "departementCode": venue.departementCode,
            "city": venue.city,
        }
        # same behavior as when update_venue() is called from PC Pro API
        contact_data = serialize_base.VenueContactModel(email=None, phone_number=None, social_medias=None, website=None)

        offerers_api.update_venue(venue, contact_data=contact_data, author=user, **venue_data)

        # then
        # nothing has changed => nothing to save nor update
        assert history_models.ActionHistory.query.count() == 0

    def test_no_venue_contact_add_contact(self, app) -> None:
        # given
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(contact=None)

        # when
        venue_data = {
            "departementCode": venue.departementCode,
            "city": venue.city,
        }
        # same behavior as when update_venue() is called from PC Pro API
        contact_data = serialize_base.VenueContactModel(
            email="added@venue.com", phone_number=None, social_medias=None, website="https://www.venue.com"
        )

        offerers_api.update_venue(venue, contact_data=contact_data, author=user, **venue_data)

        # then
        assert venue.contact
        assert venue.contact.email == contact_data.email
        assert venue.contact.website == contact_data.website

        # contact info added => an action should be logged in history
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.authorUserId == user.id
        assert action.venueId == venue.id
        assert action.extraData["modified_info"] == {
            "contact.email": {"new_info": contact_data.email, "old_info": "None"},
            "contact.website": {"new_info": contact_data.website, "old_info": "None"},
        }

    def test_edit_reimbursement_point_id(self):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(pricing_point="self")
        reimbursement_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.BankInformationFactory(venue=reimbursement_point)
        venue_data = {
            "reimbursementPointId": reimbursement_point.id,
        }
        offerers_api.update_venue(venue, author=user, **venue_data)

        assert venue.current_reimbursement_point_id == reimbursement_point.id


class EditVenueContactTest:
    def test_create_venue_contact(self, app):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        contact_data = serialize_base.VenueContactModel(
            email="contact@venue.com",
            phone_number="+33766778899",
            social_medias={"instagram": "https://instagram.com/@venue"},
        )

        venue = offerers_api.upsert_venue_contact(venue, contact_data)

        assert venue.contact
        assert venue.contact.email == contact_data.email
        assert venue.contact.phone_number == contact_data.phone_number
        assert venue.contact.social_medias == contact_data.social_medias

    def test_update_venue_contact(self, app):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        contact_data = serialize_base.VenueContactModel(
            email="other.contact@venue.com", socialMedias={"instagram": "https://instagram.com/@venue"}
        )

        venue = offerers_api.upsert_venue_contact(venue, contact_data)

        assert venue.contact
        assert venue.contact.email == contact_data.email
        assert venue.contact.social_medias == contact_data.social_medias
        assert not venue.contact.phone_number


class ApiKeyTest:
    def test_generate_and_save_api_key(self):
        offerer = offerers_factories.OffererFactory()
        generated_key = offerers_api.generate_and_save_api_key(offerer.id)

        found_api_key = offerers_api.find_api_key(generated_key)

        assert found_api_key.offerer == offerer

    def test_get_provider_from_api_key(self):
        value = "a very secret legacy key"
        offerer = offerers_factories.OffererFactory()
        provider = providers_factories.ProviderFactory(localClass=None, name="RiotRecords")
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(
            offerer=offerer, provider=provider, prefix="development_a very s", secret="ecret legacy key"
        )
        with assert_num_queries(1):
            found_api_key = offerers_api.find_api_key(value)
            assert found_api_key.provider == provider

    def test_legacy_api_key(self):
        value = "a very secret legacy key"
        key = offerers_factories.ApiKeyFactory(prefix="development_a very s", secret="ecret legacy key")

        found_api_key = offerers_api.find_api_key(value)

        assert found_api_key == key

    def test_no_key_found(self):
        assert not offerers_api.find_api_key("")
        assert not offerers_api.find_api_key("idonotexist")
        assert not offerers_api.find_api_key("development_prefix_value")


class CreateOffererTest:
    def test_create_new_offerer_with_validation_token_if_siren_is_not_already_registered(self):
        # Given
        gen_offerer_tags()
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="777084112", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name
        assert created_offerer.siren == offerer_informations.siren
        assert created_offerer.address == offerer_informations.address
        assert created_offerer.postalCode == offerer_informations.postalCode
        assert created_offerer.city == offerer_informations.city
        assert created_offerer.validationStatus == ValidationStatus.NEW
        assert created_offerer.isActive
        assert "Collectivité" in (tag.label for tag in created_offerer.tags)

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert created_user_offerer.dateCreated is not None

        assert not created_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

    def test_create_digital_venue_if_siren_is_not_already_registered(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert len(created_offerer.managedVenues) == 1
        assert created_offerer.managedVenues[0].isVirtual is True

    def test_create_new_offerer_attachment_with_validation_token_if_siren_is_already_registered(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren)

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer.name
        assert created_offerer.isValidated
        assert created_offerer.isActive

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        assert created_user_offerer.dateCreated is not None

        assert not created_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == offerer

    def test_keep_offerer_validation_token_if_siren_is_already_registered_but_not_validated(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.NotValidatedOffererFactory(
            siren=offerer_informations.siren, validationStatus=ValidationStatus.PENDING
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer.name
        assert created_offerer.validationStatus == ValidationStatus.PENDING
        assert not created_offerer.isValidated

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        assert created_user_offerer.dateCreated is not None

    def test_create_new_offerer_with_validation_token_if_siren_was_previously_rejected(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name="Rejected Offerer",
            siren=offerer_informations.siren,
        )
        first_creation_date = offerer.dateCreated

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.id == offerer.id
        assert created_offerer.name == offerer_informations.name
        assert created_offerer.siren == offerer_informations.siren
        assert created_offerer.address == offerer_informations.address
        assert created_offerer.postalCode == offerer_informations.postalCode
        assert created_offerer.city == offerer_informations.city
        assert created_offerer.validationStatus == ValidationStatus.NEW
        assert created_offerer.isActive
        assert created_offerer.dateCreated > first_creation_date

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert created_user_offerer.dateCreated is not None

        assert not created_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

    def test_create_offerer_auto_tagging_no_error_if_tag_not_in_db(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="777084112", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name

    @override_settings(NATIONAL_PARTNERS_EMAIL_DOMAINS="howdy.com,partner.com")
    def test_create_offerer_national_partner_autotagging(self):
        # Given
        national_partner_tag = offerers_factories.OffererTagFactory(name="partenaire-national")
        not_a_parner_user = users_factories.UserFactory(email="noël.flantier@gmail.com")
        partner_user = users_factories.UserFactory(email="ssap.erutluc@partner.com")
        not_a_partner_offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer Not Partner",
            siren="777084112",
            address="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )
        partner_offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer Partner",
            siren="777084121",
            address="123 rue de Paname",
            postalCode="93100",
            city="Montreuil",
        )

        # When
        created_user_offerer_not_partner = offerers_api.create_offerer(
            not_a_parner_user, not_a_partner_offerer_informations
        )
        created_user_offerer_partner = offerers_api.create_offerer(partner_user, partner_offerer_informations)

        # Then
        created_offerer_not_partner = created_user_offerer_not_partner.offerer
        created_offerer_partner = created_user_offerer_partner.offerer

        assert national_partner_tag not in created_offerer_not_partner.tags
        assert national_partner_tag in created_offerer_partner.tags


class UpdateOffererTest:
    def test_update_offerer(self):
        offerer = offerers_factories.OffererFactory(city="Portus Namnetum", address="1 rue d'Armorique")

        offerers_api.update_offerer(offerer, city="Nantes", postal_code="44000", address="29 avenue de Bretagne")
        offerer = offerers_models.Offerer.query.one()
        assert offerer.city == "Nantes"
        assert offerer.postalCode == "44000"
        assert offerer.address == "29 avenue de Bretagne"

        offerers_api.update_offerer(offerer, city="Naoned")
        offerer = offerers_models.Offerer.query.one()
        assert offerer.city == "Naoned"
        assert offerer.postalCode == "44000"
        assert offerer.address == "29 avenue de Bretagne"

    def test_update_offerer_returns_modified_info(self):
        offerer = offerers_factories.OffererFactory(city="Portus Namnetum", address="1 rue d'Armorique")

        modified_info = offerers_api.update_offerer(offerer, city="Nantes", address="29 avenue de Bretagne")
        assert modified_info == {
            "city": {"new_info": "Nantes", "old_info": "Portus Namnetum"},
            "address": {"new_info": "29 avenue de Bretagne", "old_info": "1 rue d'Armorique"},
        }


class SearchOffererTest:
    def test_search_offerer(self):
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory(name=f"Musée Magique {offerer1.id}")

        search_result = offerers_api.search_offerer(search_query=str(offerer1.id)).all()
        assert len(search_result) == 1
        assert offerer1 in search_result

        search_result = offerers_api.search_offerer(search_query=offerer2.name).all()
        assert offerer2 in search_result


class ValidateOffererAttachmentTest:
    def test_offerer_attachment_is_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment(user_offerer, admin)

        # Then
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED

    def test_pro_role_is_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment(user_offerer, admin)

        # Then
        assert applicant.has_pro_role
        assert not applicant.has_non_attached_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_validation_email_to_pro")
    def test_send_validation_confirmation_email(self, mocked_send_validation_confirmation_email_to_pro):
        # Given
        admin = users_factories.AdminFactory()
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment(user_offerer, admin)

        # Then
        mocked_send_validation_confirmation_email_to_pro.assert_called_once_with(user_offerer)


@freeze_time("2020-10-15 00:00:00")
class RejectOffererAttachementTest:
    def test_offerer_attachement_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        assert offerers_models.UserOfferer.query.count() == 0

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_rejection_email_to_pro", return_value=True)
    def test_send_rejection_confirmation_email(self, send_offerer_attachment_rejection_email_to_pro):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        send_offerer_attachment_rejection_email_to_pro.assert_called_once_with(user_offerer)

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user, offerer=offerer)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None


@freeze_time("2020-10-15 00:00:00")
class ValidateOffererTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        assert user_offerer.offerer.isValidated
        assert user_offerer.offerer.dateValidated == datetime.datetime.utcnow()
        assert user_offerer.offerer.validationStatus == ValidationStatus.VALIDATED

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated_mail_sent(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        venue1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, adageId="11")
        mails = get_emails_by_venue(venue1)

        # When
        with patch("pcapi.core.offerers.api.send_eac_offerer_activation_email") as mock_activation_mail:
            offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        mock_activation_mail.assert_called_with(venue1, list(mails))

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_pro_role_is_added_to_user(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        another_applicant = users_factories.UserFactory()
        another_user_on_same_offerer = offerers_factories.NotValidatedUserOffererFactory(user=another_applicant)

        # When
        offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        assert user_offerer.user.has_pro_role
        assert not another_applicant.has_pro_role
        assert not another_user_on_same_offerer.isValidated
        assert not user_offerer.user.has_non_attached_pro_role

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_managed_venues_are_reindexed(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # When
        offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once()
        called_args, _ = mocked_async_index_offers_of_venue_ids.call_args
        assert set(called_args[0]) == {venue_1.id, venue_2.id}

    @patch("pcapi.core.mails.transactional.send_new_offerer_validation_email_to_pro", return_value=True)
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_send_validation_confirmation_email(
        self, mocked_async_index_offers_of_venue_ids, mocked_send_new_offerer_validation_email_to_pro
    ):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        mocked_send_new_offerer_validation_email_to_pro.assert_called_once_with(user_offerer.offerer)

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_action_is_logged(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer(user_offerer.offerer, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None


@freeze_time("2020-10-15 00:00:00")
class RejectOffererTest:
    def test_offerer_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer, admin)

        # Then
        assert not offerer.isValidated
        assert offerer.dateValidated is None
        assert offerer.validationStatus == ValidationStatus.REJECTED

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=user)

        # When
        offerers_api.reject_offerer(user_offerer.offerer, admin)

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer(user_offerer.offerer, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role
        assert not validated_user_offerer.user.has_non_attached_pro_role

    def test_attachment_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.reject_offerer(user_offerer.offerer, admin)

        # Then
        assert offerers_models.UserOfferer.query.count() == 0

    def test_api_key_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        offerers_api.reject_offerer(user_offerer.offerer, admin)

        # Then
        assert offerers_models.UserOfferer.query.count() == 0
        assert offerers_models.ApiKey.query.count() == 0

    @patch("pcapi.core.mails.transactional.send_new_offerer_rejection_email_to_pro", return_value=True)
    def test_send_rejection_confirmation_email(self, send_new_offerer_rejection_email_to_pro):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer, admin)

        # Then
        send_new_offerer_rejection_email_to_pro.assert_called_once_with(offerer)

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # removed in reject_offerer()
        offerers_factories.UserOffererFactory(
            offerer=offerer, validationStatus=ValidationStatus.NEW
        )  # another applicant

        # When
        offerers_api.reject_offerer(offerer, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None


def test_grant_user_offerer_access():
    offerer = offerers_factories.OffererFactory.build()
    user = users_factories.UserFactory.build()

    user_offerer = offerers_api.grant_user_offerer_access(offerer, user)

    assert user_offerer.user == user
    assert user_offerer.offerer == offerer
    assert user_offerer.validationStatus == ValidationStatus.VALIDATED
    assert not user.has_pro_role


class VenueBannerTest:
    IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"

    @freeze_time("2020-10-15 00:00:00")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_save_venue_banner_when_no_default_available(self, mock_search_async_index_venue_ids, tmpdir):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            offerers_api.save_venue_banner(user, venue, image_content, image_credit="none")

            updated_venue = Venue.query.get(venue.id)
            with open(updated_venue.bannerUrl, mode="rb") as f:
                # test that image size has been reduced
                assert len(f.read()) < len(image_content)

            assert updated_venue.bannerMeta == {
                "author_id": user.id,
                "image_credit": "none",
                "original_image_url": str(directory / f"{humanize(venue.id)}_1602720001"),
                "crop_params": None,
                "updated_at": "2020-10-15T00:00:00",
            }

            mock_search_async_index_venue_ids.assert_called_once_with([venue.id])

    @freeze_time("2020-10-15 00:00:00")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_save_venue_banner_when_default_available(self, mock_search_async_index_venue_ids, tmpdir):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.MOVIE)
        image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            offerers_api.save_venue_banner(user, venue, image_content, image_credit="none")

            updated_venue = Venue.query.get(venue.id)
            with open(updated_venue.bannerUrl, mode="rb") as f:
                # test that image size has been reduced
                assert len(f.read()) < len(image_content)

            assert updated_venue.bannerMeta == {
                "author_id": user.id,
                "image_credit": "none",
                "original_image_url": str(directory / f"{humanize(venue.id)}_1602720001"),
                "crop_params": None,
                "updated_at": "2020-10-15T00:00:00",
            }

            mock_search_async_index_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_venue_ids")
    def test_replace_venue_banner(self, mock_search_async_index_venue_ids, tmpdir):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        first_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        second_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_landscape.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            with freeze_time("2020-10-15 00:00:00"):
                offerers_api.save_venue_banner(user, venue, first_image_content, image_credit="first_image")

            with freeze_time("2020-10-15 00:00:05"):
                offerers_api.save_venue_banner(user, venue, second_image_content, image_credit="second_image")

            files = set(os.listdir(directory))

            # old banner and its original image
            assert f"{humanize(venue.id)}_1602720000" not in files
            assert f"{humanize(venue.id)}_1602720001" not in files

            # new banner and its original image
            assert f"{humanize(venue.id)}_1602720005" in files
            assert f"{humanize(venue.id)}_1602720006" in files

    @patch("pcapi.core.search.async_index_venue_ids")
    def test_replace_venue_legacy_banner(self, mock_search_async_index_venue_ids, tmpdir):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        first_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        second_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_landscape.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            with freeze_time("2020-10-15 00:00:00"):
                offerers_api.save_venue_banner(user, venue, first_image_content, image_credit="first_image")
                move_venue_banner_to_legacy_location(venue, directory, "1602720000")
            with freeze_time("2020-10-15 00:00:01"):
                offerers_api.save_venue_banner(user, venue, second_image_content, image_credit="second_image")

            files = set(os.listdir(directory))
            assert f"{humanize(venue.id)}" not in files
            assert f"{humanize(venue.id)}_1602720001" in files


def move_venue_banner_to_legacy_location(venue, directory, timestamp):
    venue.bannerUrl = venue.bannerUrl.split("_")[0]
    os.rename(directory / f"{humanize(venue.id)}_{timestamp}", directory / f"{humanize(venue.id)}")
    os.rename(directory / f"{humanize(venue.id)}_{timestamp}.type", directory / f"{humanize(venue.id)}.type")


class GetEligibleForSearchVenuesTest:
    def test_get_all_eligibles_venues_by_default(self) -> None:
        eligible_venues = offerers_factories.VenueFactory.create_batch(3, isPermanent=True)

        with assert_num_queries(1):
            venues = list(offerers_api.get_eligible_for_search_venues())

        assert {venue.id for venue in venues} == {venue.id for venue in eligible_venues}

    def test_max_limit_number_of_venues(self) -> None:
        eligible_venues = offerers_factories.VenueFactory.create_batch(3, isPermanent=True)

        with assert_num_queries(1):
            venues = list(offerers_api.get_eligible_for_search_venues(max_venues=1))

        assert venues[0].id in {venue.id for venue in eligible_venues}

    def test_only_permantent_venues_are_eligibles(self) -> None:
        eligible_venues = offerers_factories.VenueFactory.create_batch(3, isPermanent=True)
        offerers_factories.VirtualVenueFactory.create_batch(2)  # non-eligible venues

        venues = list(offerers_api.get_eligible_for_search_venues())

        assert {venue.id for venue in venues} == {venue.id for venue in eligible_venues}


class LinkVenueToPricingPointTest:
    def test_no_pre_existing_link(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        assert offerers_models.VenuePricingPointLink.query.count() == 0

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)

        new_link = offerers_models.VenuePricingPointLink.query.one()
        assert new_link.venue == venue
        assert new_link.pricingPoint == pricing_point
        assert new_link.timespan.upper is None

    def test_raises_if_pre_existing_link(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        pricing_point_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=pricing_point_1)
        pre_existing_link = offerers_models.VenuePricingPointLink.query.one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with pytest.raises(offerers_exceptions.CannotLinkVenueToPricingPoint):
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id)
        assert offerers_models.VenuePricingPointLink.query.one() == pre_existing_link

    def test_raises_if_venue_has_siret(self):
        venue = offerers_factories.VenueFactory(siret="1234", pricing_point="self")
        pre_existing_link = offerers_models.VenuePricingPointLink.query.one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with pytest.raises(api_errors.ApiErrors):
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id)
        assert offerers_models.VenuePricingPointLink.query.one() == pre_existing_link

    def test_fails_if_venue_has_siret(self):
        reimbursement_point = offerers_factories.VenueFactory()
        offerer = reimbursement_point.managingOfferer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="1234")

        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.link_venue_to_pricing_point(venue, reimbursement_point.id)
        msg = "Ce lieu a un SIRET, vous ne pouvez donc pas choisir un autre lieu pour le calcul du barème de remboursement."
        assert error.value.errors == {"pricingPointId": [msg]}


class LinkVenueToReimbursementPointTest:
    def test_no_pre_existing_link(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        reimbursement_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.BankInformationFactory(venue=reimbursement_point)
        assert offerers_models.VenueReimbursementPointLink.query.count() == 0

        offerers_api.link_venue_to_reimbursement_point(venue, reimbursement_point.id)

        new_link = offerers_models.VenueReimbursementPointLink.query.one()
        assert new_link.venue == venue
        assert new_link.reimbursementPoint == reimbursement_point
        assert new_link.timespan.upper is None

    @freeze_time()
    def test_end_pre_existing_link(self):
        now = datetime.datetime.utcnow()
        venue = offerers_factories.VenueFactory(reimbursement_point="self", pricing_point="self")
        offerers_api.link_venue_to_reimbursement_point(venue, None)

        former_link = offerers_models.VenueReimbursementPointLink.query.one()
        assert former_link.venue == venue
        assert former_link.reimbursementPoint == venue
        assert former_link.timespan.upper == now

    def test_pre_existing_links(self):
        now = datetime.datetime.utcnow()
        venue = offerers_factories.VenueFactory(pricing_point="self")
        reimbursement_point_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.BankInformationFactory(venue=reimbursement_point_1)
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=reimbursement_point_1,
            timespan=[
                now - datetime.timedelta(days=10),
                now - datetime.timedelta(days=3),
            ],
        )
        reimbursement_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.BankInformationFactory(venue=reimbursement_point_2)
        offerers_factories.VenueReimbursementPointLinkFactory(
            venue=venue,
            reimbursementPoint=reimbursement_point_2,
            timespan=[
                now - datetime.timedelta(days=1),
                None,
            ],
        )
        current_link = offerers_models.VenueReimbursementPointLink.query.order_by(sa.desc("id")).first()
        reimbursement_point_3 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        finance_factories.BankInformationFactory(venue=reimbursement_point_3)

        offerers_api.link_venue_to_reimbursement_point(venue, reimbursement_point_3.id)

        assert offerers_models.VenueReimbursementPointLink.query.count() == 3
        new_link = offerers_models.VenueReimbursementPointLink.query.order_by(sa.desc("id")).first()
        assert new_link.venue == venue
        assert new_link.reimbursementPoint == reimbursement_point_3
        assert new_link.timespan.lower == current_link.timespan.upper
        assert new_link.timespan.upper is None

    def test_fails_if_reimbursement_point_has_no_bank_information(self):
        reimbursement_point = offerers_factories.VenueFactory()
        offerer = reimbursement_point.managingOfferer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")

        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.link_venue_to_reimbursement_point(venue, reimbursement_point.id)
        msg = f"Le lieu {reimbursement_point.name} ne peut pas être utilisé pour les remboursements car il n'a pas de coordonnées bancaires validées."
        assert error.value.errors == {"reimbursementPointId": [msg]}


class HasVenueAtLeastOneBookableOfferTest:
    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_eligible(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offers_factories.EventStockFactory(offer__venue=venue)

        assert offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_no_offers(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_managing_offerer_not_validated(self):
        venue = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer=offerers_factories.NotValidatedOffererFactory()
        )
        offers_factories.EventStockFactory(offer__venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_offer_without_stock(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offers_factories.OfferFactory(venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_expired_event(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)

        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        offers_factories.EventStockFactory(beginningDatetime=one_week_ago, offer__venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @override_features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_only_one_bookable_offer(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)

        # offer with bookable stock: venue is eligible
        offers_factories.EventStockFactory(offer__venue=venue)

        # without the previous offer, the venue would not be eligible
        one_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)
        offers_factories.EventStockFactory(beginningDatetime=one_week_ago, offer__venue=venue)

        assert offerers_api.has_venue_at_least_one_bookable_offer(venue)


@freeze_time("2022-10-11 12:00:00")
@override_settings(METABASE_SECRET_KEY="metabase secret key")
def test_get_offerer_stats_dashboard_url():
    venue = offerers_factories.VenueFactory()
    offerer = venue.managingOfferer

    url = offerers_api.get_metabase_stats_iframe_url(offerer, venues=[venue])

    token = url.split("/")[3].split("#")[0]
    payload = jwt.decode(token, "metabase secret key", algorithms="HS256")
    assert payload == {
        "resource": {"dashboard": 438},
        "params": {"siren": [offerer.siren], "venueid": [str(venue.id)]},
        "exp": round(time.time()) + 600,
    }


class CountOfferersByValidationStatusTest:
    def test_get_offerer_stats(self, client):
        # given
        offerers_factories.UserOffererFactory(offerer__validationStatus=ValidationStatus.NEW)
        offerers_factories.UserOffererFactory.create_batch(2, offerer__validationStatus=ValidationStatus.PENDING)
        offerers_factories.UserOffererFactory.create_batch(3, offerer__validationStatus=ValidationStatus.VALIDATED)
        offerers_factories.UserOffererFactory.create_batch(4, offerer__validationStatus=ValidationStatus.REJECTED)

        # when
        with assert_num_queries(1):
            stats = offerers_api.count_offerers_by_validation_status()

        # then
        assert stats == {"NEW": 1, "PENDING": 2, "VALIDATED": 3, "REJECTED": 4}

    def test_get_offerer_stats_zero(self, client):
        # when
        with assert_num_queries(1):
            stats = offerers_api.count_offerers_by_validation_status()

        # then
        assert stats == {"NEW": 0, "PENDING": 0, "VALIDATED": 0, "REJECTED": 0}


class UpdateOffererTagTest:
    def test_update_offerer_tag(self):
        offerer_tag = offerers_factories.OffererTagFactory(name="serious-tag-name", label="Serious Tag")

        offerers_api.update_offerer_tag(
            offerer_tag, name="not-so-serious-tag-name", label="Taggy McTagface", description="Why so serious ?"
        )
        offerer_tag = offerers_models.OffererTag.query.one()
        assert offerer_tag.name == "not-so-serious-tag-name"
        assert offerer_tag.label == "Taggy McTagface"
        assert offerer_tag.description == "Why so serious ?"


class CreateFromOnboardingDataTest:
    def assert_common_venue_attrs(self, venue: offerers_models.Venue) -> None:
        assert venue.address == "3 RUE DE VALOIS"
        assert venue.bookingEmail == "pro@example.com"
        assert venue.city == "Paris"
        assert not venue.current_reimbursement_point_id
        assert venue.dmsToken
        assert venue.latitude == decimal.Decimal("2.30829")
        assert venue.longitude == decimal.Decimal("48.87171")
        assert venue.name == "MINISTERE DE LA CULTURE"
        assert venue.postalCode == "75001"
        assert venue.publicName == "Nom public de mon lieu"
        assert venue.venueTypeCode == offerers_models.VenueTypeCode.MOVIE
        assert venue.audioDisabilityCompliant is None
        assert venue.mentalDisabilityCompliant is None
        assert venue.motorDisabilityCompliant is None
        assert venue.visualDisabilityCompliant is None

    def assert_common_action_history_extra_data(self, action: history_models.ActionHistory) -> None:
        assert action.extraData["target"] == offerers_models.Target.INDIVIDUAL.name
        assert action.extraData["venue_type_code"] == offerers_models.VenueTypeCode.MOVIE.name
        assert (
            action.extraData["web_presence"]
            == "https://www.example.com, https://instagram.com/example, https://mastodon.social/@example"
        )

    def assert_only_welcome_email_to_pro_was_sent(self) -> None:
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]["id_not_prod"] == TransactionalEmail.WELCOME_TO_PRO.value.id
        )

    def get_onboarding_data(
        self, create_venue_without_siret: bool
    ) -> offerers_serialize.SaveNewOnboardingDataQueryModel:
        return offerers_serialize.SaveNewOnboardingDataQueryModel(
            address="3 RUE DE VALOIS",
            city="Paris",
            createVenueWithoutSiret=create_venue_without_siret,
            latitude=2.30829,
            longitude=48.87171,
            postalCode="75001",
            publicName="Nom public de mon lieu",
            siret="85331845900031",
            target=offerers_models.Target.INDIVIDUAL,
            venueTypeCode=offerers_models.VenueTypeCode.MOVIE.name,
            webPresence="https://www.example.com, https://instagram.com/example, https://mastodon.social/@example",
        )

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_new_siren_new_siret(self):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.address == "3 RUE DE VALOIS"
        assert created_offerer.postalCode == "75001"
        assert created_offerer.city == "Paris"
        assert created_offerer.validationStatus == ValidationStatus.NEW
        # User is attached to offerer
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        # but does not have PRO role yet, because the Offerer is not validated
        assert created_user_offerer.user.has_non_attached_pro_role
        # 1 virtual Venue + 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 2
        created_venue, created_virtual_venue = sorted(
            created_user_offerer.offerer.managedVenues, key=lambda v: v.isVirtual
        )
        assert created_virtual_venue.isVirtual
        self.assert_common_venue_attrs(created_venue)
        assert created_venue.comment is None
        assert created_venue.siret == "85331845900031"
        assert created_venue.current_pricing_point_id == created_venue.id
        # Action logs
        assert history_models.ActionHistory.query.count() == 1
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.OFFERER_NEW
        ).one()
        assert offerer_action.offerer == created_offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        self.assert_only_welcome_email_to_pro_was_sent()

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_existing_siren_new_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert offerers_models.Offerer.query.count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        assert created_user_offerer.user.has_non_attached_pro_role
        # 1 venue with siret has been created
        assert len(offerer.managedVenues) == 2
        created_venue = next(v for v in offerer.managedVenues if not v.isVirtual)
        self.assert_common_venue_attrs(created_venue)
        assert created_venue.comment is None
        assert created_venue.siret == "85331845900031"
        assert created_venue.current_pricing_point_id == created_venue.id
        # Action logs
        assert history_models.ActionHistory.query.count() == 1
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW
        ).one()
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        self.assert_only_welcome_email_to_pro_was_sent()

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_existing_siren_new_venue_without_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=True)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert offerers_models.Offerer.query.count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.user.has_non_attached_pro_role
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        # 1 venue without siret has been created
        assert len(offerer.managedVenues) == 2
        created_venue = next(v for v in offerer.managedVenues if not v.isVirtual)
        self.assert_common_venue_attrs(created_venue)
        assert created_venue.comment == "Lieu sans SIRET car dépend du SIRET d'un autre lieu"
        assert created_venue.siret is None
        # No pricing point yet
        assert not created_venue.current_pricing_point_id
        # Action logs
        assert history_models.ActionHistory.query.count() == 1
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW
        ).one()
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        self.assert_only_welcome_email_to_pro_was_sent()

    @override_features(WIP_ENABLE_NEW_ONBOARDING=True)
    def test_existing_siren_existing_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        _virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)
        _venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, siret="85331845900031")
        user = users_factories.UserFactory()
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert offerers_models.Offerer.query.count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.user.has_non_attached_pro_role
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        # Venue has not been created
        assert offerers_models.Venue.query.count() == 2
        # Action logs
        assert history_models.ActionHistory.query.count() == 1
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW
        ).one()
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        self.assert_only_welcome_email_to_pro_was_sent()
