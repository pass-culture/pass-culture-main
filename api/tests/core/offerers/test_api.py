import datetime
import os
import pathlib
from unittest.mock import patch

from freezegun import freeze_time
import pytest
import sqlalchemy as sa

from pcapi.connectors import sirene
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
import pcapi.core.offerers.exceptions as offerers_exceptions
from pcapi.core.offerers.models import ApiKey
from pcapi.core.offerers.models import Venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.models import api_errors
from pcapi.routes.serialization import base as serialize_base
from pcapi.routes.serialization import venues_serialize
from pcapi.routes.serialization.offerers_serialize import CreateOffererQueryModel
from pcapi.utils.human_ids import humanize

import tests


pytestmark = pytest.mark.usefixtures("db_session")


class CreateVenueTest:
    def base_data(self, offerer):
        return {
            "address": "rue du test",
            "city": "Paris",
            "postalCode": "75000",
            "latitude": 1,
            "longitude": 1,
            "managingOffererId": humanize(offerer.id),
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

    def test_with_business_unit(self):
        offerer = offerers_factories.OffererFactory()
        business_unit = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            siret=offerer.siren + "12345",
        ).businessUnit
        data = dict(self.base_data(offerer), businessUnitId=business_unit.id)
        offerers_api.create_venue(venues_serialize.PostVenueBodyModel(**data))

        venue = offerers_models.Venue.query.order_by(offerers_models.Venue.id.desc()).first()
        assert venue.businessUnit == business_unit
        links = [link for link in business_unit.venue_links if link.venueId == venue.id]
        assert len(links) == 1


class EditVenueTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def when_changes_on_name_algolia_indexing_is_triggered(self, mocked_async_index_offers_of_venue_ids):
        # Given
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory()

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
        venue = offerers_factories.VenueFactory(
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
        venue = offerers_factories.VenueFactory()

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
            offerers_api.update_venue(venue, contact_data, **venue_data)

    def test_update_only_venue_contact(self, app):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        contact_data = serialize_base.VenueContactModel(email="other.contact@venue.com", phone_number="0788888888")

        offerers_api.update_venue(venue, contact_data)

        venue = offerers_models.Venue.query.get(venue.id)
        assert venue.contact
        assert venue.contact.phone_number == contact_data.phone_number
        assert venue.contact.email == contact_data.email

    def test_update_venue_holder_business_unit(self):
        offerer = offerers_factories.OffererFactory(siren="000000000")
        venue = offerers_factories.VenueFactory(
            siret="00000000000011", businessUnit__siret="00000000000011", managingOfferer=offerer
        )
        deleted_business_unit = venue.businessUnit
        offerers_factories.VenueFactory(
            siret="00000000000012", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offerers_factories.VenueFactory(
            siret="00000000000013", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offerers_factories.VenueFactory(
            siret="00000000000014", businessUnit=deleted_business_unit, managingOfferer=offerer
        )
        offerers_factories.VenueFactory(siret="00000000000015", managingOfferer=offerer)

        business_unit = finance_factories.BusinessUnitFactory(siret="00000000000013")

        venue_data = {"businessUnitId": business_unit.id}

        offerers_api.update_venue(venue, **venue_data)

        assert venue.businessUnitId == business_unit.id
        assert deleted_business_unit.status == finance_models.BusinessUnitStatus.DELETED
        assert offerers_models.Venue.query.filter(offerers_models.Venue.businessUnitId.is_(None)).count() == 3
        links = (
            finance_models.BusinessUnitVenueLink.query.filter_by(venueId=venue.id)
            .order_by(finance_models.BusinessUnitVenueLink.id)
            .all()
        )
        assert len(links) == 2
        assert links[0].timespan.upper is not None
        assert links[1].timespan.upper is None

    def test_update_virtual_venue_business_unit(self):
        offerer = offerers_factories.OffererFactory(siren="000000000")
        venue = offerers_factories.VenueFactory(siret="00000000000011", managingOfferer=offerer)
        virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        venue_data = {"businessUnitId": venue.businessUnitId}

        offerers_api.update_venue(virtual_venue, **venue_data)

        assert virtual_venue.businessUnitId == venue.businessUnitId

    def test_updating_business_unit_sets_a_new_link(self):
        venue = offerers_factories.VenueFactory(businessUnit=None)
        siren = venue.managingOfferer.siren
        business_unit = finance_factories.BusinessUnitFactory(siret=siren + "00000")

        offerers_api.update_venue(venue, businessUnitId=business_unit.id)

        assert venue.businessUnit == business_unit
        link = finance_models.BusinessUnitVenueLink.query.filter_by(venueId=venue.id).one()
        assert link.businessUnit == business_unit
        assert link.timespan.upper is None

    def test_cannot_update_virtual_venue_name(self):
        offerer = offerers_factories.OffererFactory(siren="000000000")
        virtual_venue = offerers_factories.VirtualVenueFactory(managingOfferer=offerer)

        venue_data = {"name": "Toto"}
        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.update_venue(virtual_venue, **venue_data)

        msg = "Vous ne pouvez modifier que le point de remboursement du lieu Offre Numérique."
        assert error.value.errors == {"venue": [msg]}

    def test_edit_venue_with_pending_bank_info(self):
        venue = offerers_factories.VenueFactory(
            pricing_point="self", reimbursement_point="self", publicName="Nom actuel"
        )
        finance_factories.BankInformationFactory(venue=venue, status=finance_models.BankInformationStatus.DRAFT)
        venue_data = {
            "publicName": "Nouveau nom",
            "reimbursementPointId": venue.current_reimbursement_point_id,
            # all the other venue attributes should be in this dict
        }
        offerers_api.update_venue(venue, **venue_data)

        assert venue.publicName == "Nouveau nom"


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

    def test_legacy_api_key(self):
        offerer = offerers_factories.OffererFactory()
        value = "a very secret key"
        ApiKey(value=value, offerer=offerer)

        found_api_key = offerers_api.find_api_key(value)

        assert found_api_key.offerer == offerer

    def test_no_key_found(self):
        assert not offerers_api.find_api_key("legacy-key")
        assert not offerers_api.find_api_key("development_prefix_value")


class CreateOffererTest:
    def _gen_offerer_tags(self):
        tags = [offerers_factories.OffererTagFactory(label=label) for label in ("Collectivité", "Établissement public")]
        return tags

    @patch("pcapi.domain.admin_emails.maybe_send_offerer_validation_email", return_value=True)
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
        assert created_offerer.validationStatus == offerers_models.ValidationStatus.NEW

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is None
        assert created_user_offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED

        assert not created_user_offerer.user.has_pro_role

        mock_maybe_send_offerer_validation_email.assert_called_once_with(
            created_user_offerer.offerer,
            created_user_offerer,
            sirene.get_siren(created_user_offerer.offerer.siren),
        )

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

    @patch("pcapi.domain.admin_emails.maybe_send_offerer_validation_email", return_value=True)
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

    @patch("pcapi.domain.admin_emails.maybe_send_offerer_validation_email", return_value=True)
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
        assert created_offerer.isValidated

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is not None
        assert created_user_offerer.validationStatus == offerers_models.ValidationStatus.NEW

        assert not created_user_offerer.user.has_pro_role

        mock_maybe_send_offerer_validation_email.assert_called_once_with(
            created_user_offerer.offerer,
            created_user_offerer,
            sirene.get_siren(created_user_offerer.offerer.siren),
        )

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == offerer

    @patch("pcapi.domain.admin_emails.maybe_send_offerer_validation_email", return_value=True)
    def test_keep_offerer_validation_token_if_siren_is_already_registered_but_not_validated(
        self, mock_maybe_send_offerer_validation_email
    ):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.NotValidatedOffererFactory(
            siren=offerer_informations.siren, validationStatus=offerers_models.ValidationStatus.PENDING
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer.name
        assert created_offerer.validationToken == offerer.validationToken
        assert created_offerer.validationStatus == offerers_models.ValidationStatus.PENDING
        assert not created_offerer.isValidated

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is not None
        assert created_user_offerer.validationStatus == offerers_models.ValidationStatus.NEW

    @patch("pcapi.domain.admin_emails.maybe_send_offerer_validation_email", return_value=True)
    def test_create_new_offerer_with_validation_token_if_siren_was_previously_rejected(
        self, mock_maybe_send_offerer_validation_email
    ):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(
            name="Rejected Offerer",
            siren=offerer_informations.siren,
            validationStatus=offerers_models.ValidationStatus.REJECTED,
        )

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
        assert created_offerer.validationToken is not None
        assert created_offerer.validationStatus == offerers_models.ValidationStatus.NEW

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationToken is None
        assert created_user_offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED

        assert not created_user_offerer.user.has_pro_role

        mock_maybe_send_offerer_validation_email.assert_called_once_with(
            created_user_offerer.offerer,
            created_user_offerer,
            sirene.SirenInfo(
                siren="418166096",
                name="MINISTERE DE LA CULTURE",
                head_office_siret="41816609600001",
                ape_code="90.03A",
                legal_category_code="1000",
                address=sirene._Address(street="3 RUE DE VALOIS", postal_code="75001", city="Paris"),
            ),
        )

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

    @pytest.mark.parametrize(
        "siren, expected_ape, expected_tag",
        (
            ("777084112", "84.11Z", "Collectivité"),
            ("777084122", "84.12Z", "Établissement public"),
            ("777091032", "91.03Z", "Établissement public"),
        ),
    )
    def test_create_offerer_auto_tagging(self, siren, expected_ape, expected_tag):
        # Given
        self._gen_offerer_tags()
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren=siren, address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name
        assert expected_tag in (tag.label for tag in created_offerer.tags)

    def test_create_offerer_auto_tagging_no_error_if_tag_not_in_db(self):
        # Given
        offerers_factories.VirtualVenueTypeFactory()
        user = users_factories.UserFactory()
        offerer_informations = CreateOffererQueryModel(
            name="Test Offerer", siren=777084112, address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name


class ValidateOffererAttachmentTest:
    def test_offerer_attachment_is_validated(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment_by_token(user_offerer.validationToken)

        # Then
        assert user_offerer.validationToken is None
        assert user_offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED

    def test_pro_role_is_added_to_user(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment_by_token(user_offerer.validationToken)

        # Then
        assert applicant.has_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_validation_email_to_pro")
    def test_send_validation_confirmation_email(self, mocked_send_validation_confirmation_email_to_pro):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment_by_token(user_offerer.validationToken)

        # Then
        mocked_send_validation_confirmation_email_to_pro.assert_called_once_with(user_offerer)

    def test_do_not_validate_attachment_if_token_does_not_exist(self):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=applicant, validationToken="TOKEN")

        # When
        with pytest.raises(offerers_exceptions.ValidationTokenNotFoundError):
            offerers_api.validate_offerer_attachment_by_token("OTHER TOKEN")

        # Then
        assert not applicant.has_pro_role
        assert user_offerer.validationToken == "TOKEN"


@freeze_time("2020-10-15 00:00:00")
class RejectOffererAttachementTest:
    def test_offerer_attachement_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer.id, admin)

        # Then
        assert offerers_models.UserOfferer.query.count() == 0

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer.id, admin)

        # Then
        assert not user.has_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer.id, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_rejection_email_to_pro", return_value=True)
    def test_send_rejection_confirmation_email(self, send_offerer_attachment_rejection_email_to_pro):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer.id, admin)

        # Then
        send_offerer_attachment_rejection_email_to_pro.assert_called_once_with(user_offerer)

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user, offerer=offerer)

        # When
        offerers_api.reject_offerer_attachment(user_offerer.id, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    def test_do_not_reject_if_id_not_found(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        with pytest.raises(offerers_exceptions.UserOffererNotFoundException):
            offerers_api.reject_offerer_attachment(user_offerer.id + 100, admin)

        # Then
        assert user_offerer.validationStatus == offerers_models.ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0


@freeze_time("2020-10-15 00:00:00")
class ValidateOffererByTokenTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_by_token(user_offerer.offerer.validationToken)

        # Then
        assert user_offerer.offerer.validationToken is None
        assert user_offerer.offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED
        assert user_offerer.offerer.dateValidated == datetime.datetime.utcnow()

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_pro_role_is_added_to_user(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=applicant)
        another_applicant = users_factories.UserFactory()
        another_user_on_same_offerer = offerers_factories.NotValidatedUserOffererFactory(user=another_applicant)

        # When
        offerers_api.validate_offerer_by_token(user_offerer.offerer.validationToken)

        # Then
        assert applicant.has_pro_role
        assert not another_applicant.has_pro_role
        assert another_user_on_same_offerer.validationToken is not None

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_managed_venues_are_reindexed(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=applicant)
        venue_1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # When
        offerers_api.validate_offerer_by_token(user_offerer.offerer.validationToken)

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
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_by_token(user_offerer.offerer.validationToken)

        # Then
        mocked_send_new_offerer_validation_email_to_pro.assert_called_once_with(user_offerer.offerer)

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_action_is_logged(self, mocked_async_index_offers_of_venue_ids):
        # Given
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer_by_token(user_offerer.offerer.validationToken)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId is None
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_do_not_validate_attachment_if_token_does_not_exist(self, mocked_async_index_offers_of_venue_ids):
        # Given
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(
            user=applicant, offerer__validationToken="TOKEN"
        )

        # When
        with pytest.raises(offerers_exceptions.ValidationTokenNotFoundError):
            offerers_api.validate_offerer_by_token("OTHER TOKEN")

        # Then
        assert not applicant.has_pro_role
        assert user_offerer.offerer.validationToken == "TOKEN"
        assert history_models.ActionHistory.query.count() == 0


@freeze_time("2020-10-15 00:00:00")
class ValidateOffererByIdTest:
    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer_by_id(user_offerer.offerer.id, admin)

        # Then
        assert user_offerer.offerer.isValidated
        assert user_offerer.offerer.dateValidated == datetime.datetime.utcnow()
        assert user_offerer.offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_pro_role_is_added_to_user(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        another_applicant = users_factories.UserFactory()
        another_user_on_same_offerer = offerers_factories.NotValidatedUserOffererFactory(user=another_applicant)

        # When
        offerers_api.validate_offerer_by_id(user_offerer.offerer.id, admin)

        # Then
        assert user_offerer.user.has_pro_role
        assert not another_applicant.has_pro_role
        assert not another_user_on_same_offerer.isValidated

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_managed_venues_are_reindexed(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # When
        offerers_api.validate_offerer_by_id(user_offerer.offerer.id, admin)

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
        offerers_api.validate_offerer_by_id(user_offerer.offerer.id, admin)

        # Then
        mocked_send_new_offerer_validation_email_to_pro.assert_called_once_with(user_offerer.offerer)

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_action_is_logged(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.validate_offerer_by_id(user_offerer.offerer.id, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_VALIDATED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user_offerer.user.id
        assert action.offererId == user_offerer.offerer.id
        assert action.venueId is None

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_do_not_validate_attachment_if_id_not_found(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        with pytest.raises(offerers_exceptions.OffererNotFoundException):
            offerers_api.validate_offerer_by_id(user_offerer.offerer.id + 100, admin)

        # Then
        assert not user_offerer.user.has_pro_role
        assert not user_offerer.offerer.isValidated
        assert user_offerer.offerer.validationStatus == offerers_models.ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0


@freeze_time("2020-10-15 00:00:00")
class RejectOffererTest:
    def test_offerer_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer.id, admin)

        # Then
        assert not offerer.isValidated
        assert offerer.dateValidated is None
        assert offerer.validationStatus == offerers_models.ValidationStatus.REJECTED

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=user)

        # When
        offerers_api.reject_offerer(user_offerer.offerer.id, admin)

        # Then
        assert not user.has_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer(user_offerer.offerer.id, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    def test_attachment_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.reject_offerer(user_offerer.offerer.id, admin)

        # Then
        assert offerers_models.UserOfferer.query.count() == 0

    def test_api_key_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        offerers_api.reject_offerer(user_offerer.offerer.id, admin)

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
        offerers_api.reject_offerer(offerer.id, admin)

        # Then
        send_new_offerer_rejection_email_to_pro.assert_called_once_with(offerer)

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)  # removed in reject_offerer()
        offerers_factories.UserOffererFactory(offerer=offerer)  # another applicant

        # When
        offerers_api.reject_offerer(offerer.id, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.OFFERER_REJECTED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

    def test_do_not_reject_if_id_not_found(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        with pytest.raises(offerers_exceptions.OffererNotFoundException):
            offerers_api.reject_offerer(user_offerer.offerer.id + 100, admin)

        # Then
        assert user_offerer.offerer.validationStatus == offerers_models.ValidationStatus.NEW
        assert history_models.ActionHistory.query.count() == 0


def test_grant_user_offerer_access():
    offerer = offerers_factories.OffererFactory.build()
    user = users_factories.UserFactory.build()

    user_offerer = offerers_api.grant_user_offerer_access(offerer, user)

    assert user_offerer.user == user
    assert user_offerer.offerer == offerer
    assert user_offerer.validationStatus == offerers_models.ValidationStatus.VALIDATED
    assert not user.has_pro_role


class VenueBannerTest:
    IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"

    @freeze_time("2020-10-15 00:00:00")
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_save_venue_banner(self, mock_search_async_index_venue_ids, tmpdir):
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


# FUTURE-NEW-BANK-DETAILS: remove when new bank details journey is complete
def test_set_business_unit_to_venue_id():
    venue = offerers_factories.VenueFactory()
    current_link = finance_models.BusinessUnitVenueLink.query.one()
    new_business_unit = finance_factories.BusinessUnitFactory()

    offerers_api.set_business_unit_to_venue_id(new_business_unit.id, venue.id)

    assert current_link.timespan.upper.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())
    new_link = finance_models.BusinessUnitVenueLink.query.order_by(
        finance_models.BusinessUnitVenueLink.id.desc()
    ).first()
    assert new_link.venue == venue
    assert new_link.businessUnit == new_business_unit
    assert new_link.timespan.lower == current_link.timespan.upper
    assert new_link.timespan.upper is None


def test_set_business_unit_to_venue_id_with_multiple_links():
    venue = offerers_factories.VenueFactory()
    current_link = finance_models.BusinessUnitVenueLink.query.one()
    finance_factories.BusinessUnitVenueLinkFactory(
        venue=venue,
        timespan=[  # former, inactive link
            datetime.datetime.utcnow() - datetime.timedelta(days=1000),
            datetime.datetime.utcnow() - datetime.timedelta(days=800),
        ],
    )
    new_business_unit = finance_factories.BusinessUnitFactory()

    offerers_api.set_business_unit_to_venue_id(new_business_unit.id, venue.id)

    assert current_link.timespan.upper.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())
    new_link = finance_models.BusinessUnitVenueLink.query.order_by(
        finance_models.BusinessUnitVenueLink.id.desc()
    ).first()
    assert new_link.venue == venue
    assert new_link.businessUnit == new_business_unit
    assert new_link.timespan.lower == current_link.timespan.upper
    assert new_link.timespan.upper is None


def test_delete_business_unit():
    venue = offerers_factories.VenueFactory()
    business_unit = venue.businessUnit
    link = finance_models.BusinessUnitVenueLink.query.one()
    link_initial_start_date = link.timespan.lower
    previous_link = finance_factories.BusinessUnitVenueLinkFactory(
        businessUnit=business_unit,
        venue=venue,
        timespan=(datetime.datetime(2020, 1, 1), datetime.datetime(2020, 12, 1)),
    )
    previous_link_initial_start_date = previous_link.timespan.upper

    other_venue = offerers_factories.VenueFactory()
    other_link = finance_models.BusinessUnitVenueLink.query.filter_by(venue=other_venue).one()
    other_link_initial_start_date = other_link.timespan.lower

    offerers_api.delete_business_unit(business_unit)

    assert business_unit.status == finance_models.BusinessUnitStatus.DELETED
    assert venue.businessUnit is None
    assert link.timespan.lower == link_initial_start_date
    assert link.timespan.upper.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())

    assert previous_link.timespan.upper == previous_link_initial_start_date
    assert other_link.timespan.lower == other_link_initial_start_date
    assert other_link.timespan.upper is None  # unchanged


class LinkVenueToPricingPointTest:
    def test_no_pre_existing_link(self):
        venue = offerers_factories.VenueFactory(siret=None, comment="no siret")
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        assert offerers_models.VenuePricingPointLink.query.count() == 0

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)

        new_link = offerers_models.VenuePricingPointLink.query.one()
        assert new_link.venue == venue
        assert new_link.pricingPoint == pricing_point
        assert new_link.timespan.upper is None

    def test_raises_if_pre_existing_link(self):
        venue = offerers_factories.VenueFactory(siret=None, comment="no siret")
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
