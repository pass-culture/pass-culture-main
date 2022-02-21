from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.exceptions import ValidationTokenNotFoundError
from pcapi.core.offerers.models import ApiKey
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.models import api_errors
from pcapi.routes.serialization import base as serialize_base
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel


pytestmark = pytest.mark.usefixtures("db_session")


class EditVenueTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_name_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"name": "my new name"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_public_name_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"publicName": "my new name"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_city_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "My new city"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once_with([venue.id])

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_are_not_on_algolia_fields_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids
    ):
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
            bookingEmail="old@email.com",
        )

        # When
        json_data = {"bookingEmail": "new@email.com"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_in_payload_are_same_as_previous_it_should_not_trigger_indexing(
        self, mocked_async_index_offers_of_venue_ids
    ):
        # Given
        venue = offers_factories.VenueFactory(
            name="old names",
            publicName="old name",
            city="old City",
        )

        # When
        json_data = {"city": "old City"}
        offerers_api.update_venue(venue, **json_data)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_not_called()

    def test_empty_siret_is_editable(self, app) -> None:
        # Given
        venue = offers_factories.VenueFactory(
            comment="Pas de siret",
            siret=None,
        )

        venue_data = {
            "siret": venue.managingOfferer.siren + "11111",
        }

        # when
        updated_venue = offerers_api.update_venue(venue, **venue_data)

        # Then
        assert updated_venue.siret == venue_data["siret"]

    def test_existing_siret_is_not_editable(self, app) -> None:
        # Given
        venue = offers_factories.VenueFactory()

        # when
        venue_data = {
            "siret": venue.managingOfferer.siren + "54321",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, **venue_data)

        # Then
        assert error.value.errors["siret"] == ["Vous ne pouvez pas modifier le siret d'un lieu"]

    def test_latitude_and_longitude_wrong_format(self, app) -> None:
        # given
        venue = offers_factories.VenueFactory(
            isVirtual=False,
        )

        # when
        venue_data = {
            "latitude": -98.82387,
            "longitude": "112°3534",
        }
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(venue, **venue_data)

        # Then
        assert error.value.errors["latitude"] == ["La latitude doit être comprise entre -90.0 et +90.0"]
        assert error.value.errors["longitude"] == ["Format incorrect"]

    def test_accessibility_fields_are_updated(self, app) -> None:
        # given
        venue = offers_factories.VenueFactory()

        # when
        venue_data = {
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
        }

        offerers_api.update_venue(venue, **venue_data)

        venue = offerers_models.Venue.query.get(venue.id)
        assert venue.audioDisabilityCompliant
        assert venue.mentalDisabilityCompliant
        assert venue.motorDisabilityCompliant is False
        assert venue.visualDisabilityCompliant is False

    def test_no_modifications(self, app) -> None:
        # given
        venue = offers_factories.VenueFactory()

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
            offerers_api.update_venue(venue, contact_data, **venue_data)

    def test_update_only_venue_contact(self, app):
        user_offerer = offers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        contact_data = serialize_base.VenueContactModel(email="other.contact@venue.com", phone_number="0788888888")

        offerers_api.update_venue(venue, contact_data)

        venue = offerers_models.Venue.query.get(venue.id)
        assert venue.contact
        assert venue.contact.phone_number == contact_data.phone_number
        assert venue.contact.email == contact_data.email

    def test_update_venue_holder_business_unit(self):
        offerer = offers_factories.OffererFactory(siren="000000000")
        venue = offers_factories.VenueFactory(
            siret="00000000000011", businessUnit__siret="00000000000011", managingOfferer=offerer
        )
        deleted_business_unit = venue.businessUnit
        offers_factories.VenueFactory(
            siret="00000000000012", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offers_factories.VenueFactory(
            siret="00000000000013", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offers_factories.VenueFactory(
            siret="00000000000014", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offers_factories.VenueFactory(siret="00000000000015", managingOfferer=offerer)

        business_unit = finance_factories.BusinessUnitFactory(siret="00000000000013")

        venue_data = {"businessUnitId": business_unit.id}

        offerers_api.update_venue(venue, **venue_data)

        assert venue.businessUnitId == business_unit.id
        assert deleted_business_unit.status == finance_models.BusinessUnitStatus.DELETED
        assert offerers_models.Venue.query.filter(offerers_models.Venue.businessUnitId.is_(None)).count() == 3

    def test_update_virtual_venue_business_unit(self):
        offerer = offers_factories.OffererFactory(siren="000000000")
        venue = offers_factories.VenueFactory(siret="00000000000011", managingOfferer=offerer)
        virtual_venue = offers_factories.VirtualVenueFactory(managingOfferer=offerer)

        venue_data = {"businessUnitId": venue.businessUnitId}

        offerers_api.update_venue(virtual_venue, **venue_data)

        assert virtual_venue.businessUnitId == venue.businessUnitId


class EditVenueContactTest:
    def test_create_venue_contact(self, app):
        user_offerer = offers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
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
        user_offerer = offers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

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
        offerer = offers_factories.OffererFactory()

        generated_key = offerers_api.generate_and_save_api_key(offerer.id)

        found_api_key = offerers_api.find_api_key(generated_key)

        assert found_api_key.offerer == offerer

    def test_legacy_api_key(self):
        offerer = offers_factories.OffererFactory()
        value = "a very secret key"
        ApiKey(value=value, offerer=offerer)

        found_api_key = offerers_api.find_api_key(value)

        assert found_api_key.offerer == offerer

    def test_no_key_found(self):
        assert not offerers_api.find_api_key("legacy-key")
        assert not offerers_api.find_api_key("development_prefix_value")


class CreateOffererTest:
    @patch("pcapi.core.offerers.api.maybe_send_offerer_validation_email", return_value=True)
    def test_create_new_offerer_with_validation_token_if_siren_is_not_already_registered(
        self, mock_maybe_send_offerer_validation_email
    ):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
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
        assert created_offerer.validationToken is not None

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is None

        assert not created_user_offerer.user.has_pro_role

        mock_maybe_send_offerer_validation_email.assert_called_once_with(
            created_user_offerer.offerer, created_user_offerer
        )

    @patch("pcapi.core.offerers.api.maybe_send_offerer_validation_email", return_value=True)
    def test_create_digital_venue_if_siren_is_not_already_registered(self, mock_maybe_send_offerer_validation_email):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert len(created_offerer.managedVenues) == 1
        assert created_offerer.managedVenues[0].isVirtual is True

    @patch("pcapi.core.offerers.api.maybe_send_offerer_validation_email", return_value=True)
    def test_create_new_offerer_attachment_with_validation_token_if_siren_is_already_registered(
        self, mock_maybe_send_offerer_validation_email
    ):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren)

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer.name
        assert created_offerer.validationToken is None

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is not None

        assert not created_user_offerer.user.has_pro_role

        mock_maybe_send_offerer_validation_email.assert_called_once_with(
            created_user_offerer.offerer, created_user_offerer
        )

    @patch("pcapi.core.offerers.api.maybe_send_offerer_validation_email", return_value=True)
    def test_keep_offerer_validation_token_if_siren_is_already_registered_but_not_validated(
        self, mock_maybe_send_offerer_validation_email
    ):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren, validationToken="TOKEN")

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer.name
        assert created_offerer.validationToken == "TOKEN"

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is not None


class ValidateOffererAttachmentTest:
    def test_offerer_attachment_is_validated(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, validationToken="TOKEN")

        # When
        offerers_api.validate_offerer_attachment(user_offerer.validationToken)

        # Then
        assert user_offerer.validationToken is None

    def test_pro_role_is_added_to_user(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, validationToken="TOKEN")

        # When
        offerers_api.validate_offerer_attachment(user_offerer.validationToken)

        # Then
        assert applicant.has_pro_role

    @patch("pcapi.core.offerers.api.send_offerer_attachment_validation_email_to_pro", return_value=True)
    def test_send_validation_confirmation_email(self, mocked_send_validation_confirmation_email_to_pro):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, validationToken="TOKEN")

        # When
        offerers_api.validate_offerer_attachment(user_offerer.validationToken)

        # Then
        mocked_send_validation_confirmation_email_to_pro.assert_called_once_with(user_offerer)

    def test_do_not_validate_attachment_if_token_does_not_exist(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, validationToken="TOKEN")

        # When
        with pytest.raises(ValidationTokenNotFoundError):
            offerers_api.validate_offerer_attachment("OTHER TOKEN")

        # Then
        assert not applicant.has_pro_role
        assert user_offerer.validationToken == "TOKEN"


@freeze_time("2020-10-15 00:00:00")
class ValidateOffererTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, offerer__validationToken="TOKEN")

        # When
        offerers_api.validate_offerer(user_offerer.offerer.validationToken)

        # Then
        assert user_offerer.offerer.validationToken is None
        assert user_offerer.offerer.dateValidated == datetime.utcnow()

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_pro_role_is_added_to_user(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, offerer__validationToken="TOKEN")
        another_applicant = users_factories.UserFactory()
        another_user_on_same_offerer = offers_factories.UserOffererFactory(
            user=another_applicant, validationToken="TOKEN"
        )

        # When
        offerers_api.validate_offerer(user_offerer.offerer.validationToken)

        # Then
        assert applicant.has_pro_role
        assert not another_applicant.has_pro_role
        assert another_user_on_same_offerer.validationToken is not None

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_managed_venues_are_reindexed(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, offerer__validationToken="TOKEN")
        venue_1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # When
        offerers_api.validate_offerer(user_offerer.offerer.validationToken)

        # Then
        mocked_async_index_offers_of_venue_ids.assert_called_once()
        called_args, _ = mocked_async_index_offers_of_venue_ids.call_args
        assert set(called_args[0]) == {venue_1.id, venue_2.id}

    @patch("pcapi.core.offerers.api.send_new_offerer_validation_email_to_pro", return_value=True)
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_send_validation_confirmation_email(
        self, mocked_async_index_offers_of_venue_ids, mocked_send_new_offerer_validation_email_to_pro
    ):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, offerer__validationToken="TOKEN")

        # When
        offerers_api.validate_offerer(user_offerer.offerer.validationToken)

        # Then
        mocked_send_new_offerer_validation_email_to_pro.assert_called_once_with(user_offerer.offerer)

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_do_not_validate_attachment_if_token_does_not_exist(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offers_factories.UserOffererFactory(user=applicant, offerer__validationToken="TOKEN")

        # When
        with pytest.raises(ValidationTokenNotFoundError):
            offerers_api.validate_offerer("OTHER TOKEN")

        # Then
        assert not applicant.has_pro_role
        assert user_offerer.offerer.validationToken == "TOKEN"
