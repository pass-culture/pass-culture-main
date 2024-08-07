import datetime
import decimal
import logging
import os
import pathlib
import time
from unittest.mock import patch

import jwt
import pytest
import time_machine

from pcapi.connectors import acceslibre as acceslibre_connector
from pcapi.connectors.entreprise import models as sirene_models
from pcapi.core import search
from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.bookings import models as bookings_models
from pcapi.core.criteria import factories as criteria_factories
from pcapi.core.criteria import models as criteria_models
from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational import models as educational_models
from pcapi.core.finance import factories as finance_factories
from pcapi.core.finance import models as finance_models
from pcapi.core.geography import factories as geography_factories
from pcapi.core.geography import models as geography_models
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
from pcapi.core.offers import models as offers_models
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization import base as serialize_base
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils.date import timespan_str_to_numrange
from pcapi.utils.human_ids import humanize

import tests
from tests.test_utils import gen_offerer_tags


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.mark.parametrize("ape_code, expected_tag", list(offerers_api.APE_TAG_MAPPING.items()))
def test_new_offerer_auto_tagging(db_session, ape_code, expected_tag):
    # given
    gen_offerer_tags()
    offerer = offerers_factories.OffererFactory()
    siren_info = sirene_models.SirenInfo(
        ape_code=ape_code,
        siren="777123456",
        name="this is not a name",
        head_office_siret="77712345600000",
        legal_category_code="don't know",
        active=True,
        diffusible=True,
        creation_date=datetime.date(2023, 1, 1),
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
            "street": "rue du test",
            "city": "Paris",
            "postalCode": "75000",
            "banId": "75113_1834_00007",
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
        user_offerer = offerers_factories.UserOffererFactory()
        data = venues_serialize.PostVenueBodyModel(**self.base_data(user_offerer.offerer))
        offerers_api.create_venue(data, user_offerer.user)

        venue = offerers_models.Venue.query.one()
        assert venue.street == "rue du test"
        assert venue.banId == "75113_1834_00007"
        assert venue.city == "Paris"
        assert venue.postalCode == "75000"
        assert venue.latitude == 1
        assert venue.longitude == 1
        assert venue.managingOfferer == user_offerer.offerer
        assert venue.name == "La Venue"
        assert venue.bookingEmail == "venue@example.com"
        assert venue.dmsToken
        assert venue.current_pricing_point_id == venue.id

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.VENUE_CREATED
        assert action.authorUser == user_offerer.user
        assert action.user is None
        assert action.offerer is None
        assert action.venue == venue

    def test_venue_with_no_siret_has_no_pricing_point(self):
        user_offerer = offerers_factories.UserOffererFactory()
        data = self.base_data(user_offerer.offerer) | {"siret": None, "comment": "no siret"}
        data = venues_serialize.PostVenueBodyModel(**data)

        offerers_api.create_venue(data, user_offerer.user)

        venue = offerers_models.Venue.query.one()
        assert venue.siret is None
        assert venue.current_pricing_point_id is None


class DeleteVenueTest:
    def test_delete_cascade_venue_should_abort_when_venue_has_any_bookings(self):
        # Given
        booking = bookings_factories.BookingFactory()
        venue_to_delete = booking.venue

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
            "Lieu non supprimable car il contient des réservations"
        ]
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Stock.query.count() == 1
        assert bookings_models.Booking.query.count() == 1

    def test_delete_cascade_venue_should_abort_when_venue_has_any_collective_bookings(self):
        # Given
        booking = educational_factories.CollectiveBookingFactory()
        venue_to_delete = booking.venue

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
            "Lieu non supprimable car il contient des réservations"
        ]
        assert offerers_models.Venue.query.count() == 1
        assert educational_models.CollectiveStock.query.count() == 1
        assert educational_models.CollectiveBooking.query.count() == 1

    def test_delete_cascade_venue_should_abort_when_pricing_point_for_another_venue(self):
        # Given
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer)

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteVenueUsedAsPricingPointException"] == [
            "Lieu non supprimable car il est utilisé comme point de valorisation d'un autre lieu"
        ]
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 2
        assert offerers_models.VenuePricingPointLink.query.count() == 2

    def test_delete_cascade_venue_remove_former_pricing_point_for_another_venue(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenuePricingPointLinkFactory.create_batch(
            2,  # other venues
            pricingPoint=venue_to_delete,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
                datetime.datetime.utcnow() - datetime.timedelta(days=5),
            ],
        )

        offerers_api.delete_venue(venue_to_delete.id)

        assert offerers_models.Venue.query.count() == 2
        assert offerers_models.VenuePricingPointLink.query.count() == 0

    def test_delete_cascade_venue_should_abort_when_pricing_exists_on_former_pricing_point_link(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        links = offerers_factories.VenuePricingPointLinkFactory.create_batch(
            2,
            pricingPoint=venue_to_delete,
            timespan=[
                datetime.datetime.utcnow() - datetime.timedelta(days=10),
                datetime.datetime.utcnow() - datetime.timedelta(days=5),
            ],
        )
        finance_event = finance_factories.FinanceEventFactory(
            venue=links[1].venue,
            pricingPoint=venue_to_delete,
            pricingOrderingDate=datetime.datetime.utcnow() - datetime.timedelta(days=7),
        )
        finance_factories.PricingFactory(
            booking=finance_event.booking, pricingPoint=venue_to_delete, event=finance_event
        )

        with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException):
            offerers_api.delete_venue(venue_to_delete.id)

    def test_delete_cascade_venue_should_abort_when_reimbursement_point_for_another_venue(self):
        # Given
        venue_to_delete = offerers_factories.VenueFactory(reimbursement_point="self")
        offerers_factories.VenueFactory(
            reimbursement_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer
        )

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsReimbursementPointException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteVenueUsedAsReimbursementPointException"] == [
            "Lieu non supprimable car il est utilisé comme point de remboursement d'un autre lieu"
        ]
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 2
        assert offerers_models.VenueReimbursementPointLink.query.count() == 2

    def test_delete_cascade_venue_should_remove_offers_stocks_and_activation_codes(self):
        # Given
        venue_to_delete = offerers_factories.VenueFactory()
        offers_factories.OfferFactory.create_batch(2, venue=venue_to_delete)
        stock = offers_factories.StockFactory(offer__venue=venue_to_delete)
        offers_factories.EventStockFactory(offer__venue=venue_to_delete)

        other_venue = offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)
        price_category_label = offers_factories.PriceCategoryLabelFactory(label="otherLabel", venue=other_venue)
        offers_factories.ActivationCodeFactory(stock=stock)
        stock_with_another_venue = offers_factories.EventStockFactory(
            offer__venue=other_venue,
            priceCategory__priceCategoryLabel=price_category_label,
        )
        offers_factories.ActivationCodeFactory(stock=stock_with_another_venue)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert offers_models.Stock.query.count() == 1
        assert offers_models.ActivationCode.query.count() == 1
        assert offers_models.PriceCategory.query.count() == 1
        assert offers_models.PriceCategoryLabel.query.count() == 1

    def test_delete_cascade_venue_should_remove_collective_offers_stocks_and_templates(self):
        # Given
        venue_to_delete = offerers_factories.VenueFactory()
        offer1 = educational_factories.CollectiveOfferFactory(venue=venue_to_delete)
        educational_factories.EducationalRedactorWithFavoriteCollectiveOffer(favoriteCollectiveOffers=[offer1])
        template1 = educational_factories.CollectiveOfferTemplateFactory(venue=venue_to_delete)
        educational_factories.EducationalRedactorWithFavoriteCollectiveOfferTemplate(
            favoriteCollectiveOfferTemplates=[template1]
        )
        educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue_to_delete)
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer=venue_to_delete.managingOfferer
        )
        educational_factories.CollectiveOfferRequestFactory(collectiveOfferTemplate=template1)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert educational_models.CollectiveOffer.query.count() == 1
        assert educational_models.CollectiveOfferTemplate.query.count() == 0
        assert educational_models.CollectiveStock.query.count() == 1
        assert educational_models.CollectiveOfferRequest.query.count() == 0

    def test_delete_cascade_venue_should_remove_bank_informations_of_venue(self):
        # Given
        venue_to_delete = offerers_factories.VenueFactory()
        finance_factories.BankInformationFactory(venue=venue_to_delete)
        finance_factories.BankInformationFactory()

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.Offerer.query.count() == 1
        assert finance_models.BankInformation.query.count() == 1

    def test_delete_cascade_venue_should_remove_pricing_point_links(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        offerers_api.delete_venue(venue.id)

        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.VenuePricingPointLink.query.count() == 0

    def test_delete_cascade_venue_should_remove_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory(reimbursement_point="self")

        offerers_api.delete_venue(venue.id)

        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.VenueReimbursementPointLink.query.count() == 0

    def test_delete_cascade_venue_should_remove_mediations_of_managed_offers(self):
        # Given
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offers_factories.MediationFactory(offer__venue=venue_to_delete)
        offers_factories.MediationFactory(offer__venue=venue)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert offers_models.Mediation.query.count() == 1

    def test_delete_cascade_venue_should_remove_reports_of_managed_offers(self):
        # Given
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offers_factories.OfferReportFactory(offer__venue=venue_to_delete)
        offers_factories.OfferReportFactory(offer__venue=venue)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert offers_models.OfferReport.query.count() == 1

    def test_delete_cascade_venue_should_remove_favorites_of_managed_offers(self):
        # Given
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        users_factories.FavoriteFactory(offer__venue=venue_to_delete)
        users_factories.FavoriteFactory(offer__venue=venue)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert users_models.Favorite.query.count() == 1

    def test_delete_cascade_venue_should_remove_criterions(self):
        # Given
        offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
        )
        offer_venue_to_delete = offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
        )

        # When
        offerers_api.delete_venue(offer_venue_to_delete.venue.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert criteria_models.OfferCriterion.query.count() == 1
        assert criteria_models.Criterion.query.count() == 2

    def test_delete_cascade_venue_should_remove_synchronization_to_provider(self):
        # Given
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        providers_factories.VenueProviderFactory(venue=venue_to_delete)
        providers_factories.VenueProviderFactory(venue=venue)

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert providers_models.VenueProvider.query.count() == 1
        assert providers_models.Provider.query.count() > 0

    def test_delete_cascade_venue_should_remove_synchronization_to_allocine_provider(self):
        # Given
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        providers_factories.AllocineVenueProviderFactory(venue=venue_to_delete)
        providers_factories.AllocineVenueProviderFactory(venue=venue)
        providers_factories.AllocinePivotFactory(venue=venue_to_delete)
        providers_factories.AllocinePivotFactory(venue=venue, theaterId="ABCDEFGHIJKLMNOPQR==", internalId="PABCDE")

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 1
        assert providers_models.VenueProvider.query.count() == 1
        assert providers_models.AllocineVenueProvider.query.count() == 1
        assert providers_models.AllocinePivot.query.count() == 1
        assert providers_models.Provider.query.count() > 0

    def test_delete_cascade_venue_when_template_has_offer_on_other_venue(self):
        venue = offerers_factories.VenueFactory()
        venue2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        offer = educational_factories.CollectiveOfferFactory(venue=venue2, template=template)
        offerers_api.delete_venue(venue.id)

        assert offerers_models.Venue.query.count() == 1
        assert educational_models.CollectiveOffer.query.count() == 1
        assert educational_models.CollectiveOfferTemplate.query.count() == 0
        assert offer.template is None

    def test_delete_cascade_venue_should_remove_links(self):
        # Given
        bank_account = finance_factories.BankAccountFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_to_delete, bankAccount=bank_account)
        bank_account_id = bank_account.id

        # When
        offerers_api.delete_venue(venue_to_delete.id)

        # Then
        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.VenueBankAccountLink.query.count() == 0
        assert finance_models.BankAccount.query.filter(finance_models.BankAccount.id == bank_account_id).one_or_none()

    def test_delete_cascade_venue_should_remove_adage_addresses(self):
        venue = offerers_factories.CollectiveVenueFactory()
        assert venue.adage_addresses

        offerers_api.delete_venue(venue.id)

        assert offerers_models.Venue.query.count() == 0
        assert educational_models.AdageVenueAddress.query.count() == 0

    def test_delete_cascade_venue_should_remove_playlist(self):
        venue = offerers_factories.CollectiveVenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)

        playlist = educational_factories.PlaylistFactory(venue=venue, collective_offer_template=template)
        assert playlist.venue == venue

        offerers_api.delete_venue(venue.id)

        assert offerers_models.Venue.query.count() == 0
        assert educational_models.CollectivePlaylist.query.count() == 0


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
        assert created_offerer.street == offerer_informations.street
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
        assert created_offerer.street == offerer_informations.street
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

    def test_create_new_offerer_with_validation_token_if_siren_was_previously_rejected_on_user_rejected(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name="Rejected Offerer",
            siren=offerer_informations.siren,
        )
        offerers_factories.RejectedUserOffererFactory(user=user, offerer=offerer)

        # When
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        assert offerer.validationStatus == ValidationStatus.NEW
        assert updated_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert updated_user_offerer.dateCreated is not None

        assert not updated_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

    def test_create_new_offerer_with_validation_token_if_siren_was_previously_rejected_on_user_deleted(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name="Rejected Offerer",
            siren=offerer_informations.siren,
        )
        offerers_factories.DeletedUserOffererFactory(user=user, offerer=offerer)

        # When
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        assert updated_user_offerer.offerer.validationStatus == ValidationStatus.NEW
        assert updated_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert updated_user_offerer.dateCreated is not None

        assert not updated_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

    def test_create_offerer_on_known_offerer_by_user_rejected(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren)
        offerers_factories.RejectedUserOffererFactory(user=user, offerer=offerer)

        # When
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        assert offerer.validationStatus == ValidationStatus.VALIDATED
        assert updated_user_offerer.validationStatus == ValidationStatus.NEW
        assert updated_user_offerer.dateCreated is not None

        assert not updated_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

    def test_create_offerer_on_known_offerer_twice(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren)
        offerers_factories.RejectedUserOffererFactory(user=user, offerer=offerer)

        # When
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        assert offerer.validationStatus == ValidationStatus.VALIDATED
        assert updated_user_offerer.validationStatus == ValidationStatus.NEW
        assert updated_user_offerer.dateCreated is not None

        assert not updated_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 2
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[1].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[1].authorUser == user
        assert actions_list[1].user == user
        assert actions_list[1].offerer == created_offerer

    def test_create_new_offerer_on_known_offerer_by_user_deleted(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer", siren="418166096", address="123 rue de Paris", postalCode="93100", city="Montreuil"
        )
        offerer = offerers_factories.OffererFactory(siren=offerer_informations.siren)
        offerers_factories.DeletedUserOffererFactory(user=user, offerer=offerer)

        # When
        updated_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        assert offerer.validationStatus == ValidationStatus.VALIDATED
        assert updated_user_offerer.validationStatus == ValidationStatus.NEW
        assert updated_user_offerer.dateCreated is not None

        assert not updated_user_offerer.user.has_pro_role

        actions_list = history_models.ActionHistory.query.order_by(history_models.ActionHistory.actionType).all()
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

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
        not_a_partner_user = users_factories.UserFactory(email="noël.flantier@example.com")
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
            not_a_partner_user, not_a_partner_offerer_informations
        )
        created_user_offerer_partner = offerers_api.create_offerer(partner_user, partner_offerer_informations)

        # Then
        created_offerer_not_partner = created_user_offerer_not_partner.offerer
        created_offerer_partner = created_user_offerer_partner.offerer

        assert national_partner_tag not in created_offerer_not_partner.tags
        assert national_partner_tag in created_offerer_partner.tags


class UpdateOffererTest:
    def test_update_offerer(self):
        offerer = offerers_factories.OffererFactory(city="Portus Namnetum", street="1 rue d'Armorique")
        author = users_factories.UserFactory()

        offerers_api.update_offerer(offerer, author, city="Nantes", postal_code="44000", street="29 avenue de Bretagne")
        offerer = offerers_models.Offerer.query.one()
        assert offerer.city == "Nantes"
        assert offerer.postalCode == "44000"
        assert offerer.street == "29 avenue de Bretagne"

        offerers_api.update_offerer(offerer, author, city="Naoned")
        offerer = offerers_models.Offerer.query.one()
        assert offerer.city == "Naoned"
        assert offerer.postalCode == "44000"
        assert offerer.street == "29 avenue de Bretagne"

    def test_update_offerer_logs_action(self):
        offerer = offerers_factories.OffererFactory(city="Portus Namnetum", street="1 rue d'Armorique")
        author = users_factories.UserFactory()

        offerers_api.update_offerer(offerer, author, city="Nantes", street="29 avenue de Bretagne")

        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == author.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.extraData["modified_info"] == {
            "city": {"new_info": "Nantes", "old_info": "Portus Namnetum"},
            "street": {"new_info": "29 avenue de Bretagne", "old_info": "1 rue d'Armorique"},
        }


class DeleteOffererTest:
    def test_delete_cascade_offerer_should_abort_when_offerer_has_any_bookings(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer_to_delete)

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteOffererWithBookingsException) as exception:
            offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteOffererWithBookingsException"] == [
            "Structure juridique non supprimable car elle contient des réservations"
        ]
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 2
        assert offers_models.Offer.query.count() == 2
        assert offers_models.Stock.query.count() == 1
        assert bookings_models.Booking.query.count() == 1

    def test_delete_cascade_offerer_should_abort_when_offerer_has_collective_bookings(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer_to_delete)
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer_to_delete
        )

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteOffererWithBookingsException) as exception:
            offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteOffererWithBookingsException"] == [
            "Structure juridique non supprimable car elle contient des réservations"
        ]
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 2
        assert educational_models.CollectiveOffer.query.count() == 2
        assert educational_models.CollectiveStock.query.count() == 1
        assert educational_models.CollectiveBooking.query.count() == 1

    def test_delete_cascade_offerer_should_remove_managed_venues_offers_stocks_and_activation_codes(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(venue__managingOfferer=offerer_to_delete)
        stock_1 = offers_factories.StockFactory(offer__venue__managingOfferer=offerer_to_delete)
        offers_factories.ActivationCodeFactory(stock=stock_1)
        offers_factories.EventStockFactory(offer__venue__managingOfferer=offerer_to_delete)

        other_offerer = offerers_factories.OffererFactory()

        other_venue = offerers_factories.VenueFactory(managingOfferer=other_offerer)
        stock_2 = offers_factories.StockFactory(offer__venue=other_venue)
        offers_factories.ActivationCodeFactory(stock=stock_2)
        offers_factories.EventStockFactory(offer__venue=other_venue)
        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 2
        assert offers_models.Stock.query.count() == 2
        assert offers_models.ActivationCode.query.count() == 1
        assert offers_models.PriceCategory.query.count() == 1
        assert offers_models.PriceCategoryLabel.query.count() == 1

    def test_delete_cascade_offerer_should_remove_all_user_attachments_to_deleted_offerer(self):
        # Given
        pro = users_factories.ProFactory()
        offerer_to_delete = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer_to_delete)
        offerers_factories.UserOffererFactory(user=pro)

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.UserOfferer.query.count() == 1

    def test_delete_cascade_offerer_should_remove_api_key_of_offerer(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer_to_delete)
        offerers_factories.ApiKeyFactory(prefix="other-prefix")

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.ApiKey.query.count() == 1

    def test_delete_cascade_offerer_should_remove_bank_informations_of_offerer(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        finance_factories.BankInformationFactory(offerer=offerer_to_delete)
        finance_factories.BankInformationFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 0
        assert finance_models.BankInformation.query.count() == 1

    def test_delete_cascade_offerer_should_remove_offers_of_offerer(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer_to_delete)
        offers_factories.EventOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory(venue=venue)

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 0
        assert offers_models.Offer.query.count() == 0

    def test_delete_cascade_offerer_should_remove_pricing_point_links(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue, managingOfferer=venue.managingOfferer)
        offerer = venue.managingOfferer

        offerers_api.delete_offerer(offerer.id)

        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.VenuePricingPointLink.query.count() == 0

    def test_delete_cascade_offerer_should_remove_reimbursement_point_links(self):
        venue = offerers_factories.VenueFactory(reimbursement_point="self")
        offerer = venue.managingOfferer

        offerers_api.delete_offerer(offerer.id)

        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0
        assert offerers_models.VenueReimbursementPointLink.query.count() == 0

    def test_delete_cascade_offerer_should_remove_bank_informations_of_managed_venue(self):
        # Given
        venue = offerers_factories.VenueFactory(reimbursement_point="self")
        finance_factories.BankInformationFactory(venue=venue)
        offerer_to_delete = venue.managingOfferer
        finance_factories.BankInformationFactory()
        assert finance_models.BankInformation.query.count() == 2

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 0
        assert offerers_models.Venue.query.count() == 0
        assert finance_models.BankInformation.query.count() == 1

    def test_delete_cascade_offerer_should_remove_mediations_of_managed_offers(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.MediationFactory(offer__venue__managingOfferer=offerer_to_delete)
        offers_factories.MediationFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert offers_models.Mediation.query.count() == 1

    def test_delete_cascade_offerer_should_remove_favorites_of_managed_offers(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        users_factories.FavoriteFactory(offer__venue__managingOfferer=offerer_to_delete)
        users_factories.FavoriteFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert users_models.Favorite.query.count() == 1

    def test_delete_cascade_offerer_should_remove_criterion_attachment_of_managed_offers(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.OfferFactory(
            venue__managingOfferer=offerer_to_delete,
            criteria=[criteria_factories.CriterionFactory()],
        )
        offers_factories.OfferFactory(criteria=[criteria_factories.CriterionFactory()])
        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert offers_models.Offer.query.count() == 1
        assert criteria_models.OfferCriterion.query.count() == 1
        assert criteria_models.Criterion.query.count() == 2

    def test_delete_cascade_offerer_should_remove_venue_synchronization_to_provider(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        providers_factories.VenueProviderFactory(venue__managingOfferer=offerer_to_delete)
        providers_factories.VenueProviderFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert providers_models.VenueProvider.query.count() == 1
        assert providers_models.Provider.query.count() > 0

    def test_delete_cascade_offerer_should_remove_venue_synchronization_to_allocine_provider(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        venue_to_delete = offerers_factories.VenueFactory(managingOfferer=offerer_to_delete)
        other_venue = offerers_factories.VenueFactory()
        providers_factories.AllocineVenueProviderFactory(venue=venue_to_delete)
        providers_factories.AllocineVenueProviderFactory(venue=other_venue)
        providers_factories.AllocinePivotFactory(venue=venue_to_delete)
        providers_factories.AllocinePivotFactory(
            venue=other_venue, theaterId="ABCDEFGHIJKLMNOPQR==", internalId="PABCDE"
        )

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 1
        assert offerers_models.Venue.query.count() == 1
        assert providers_models.VenueProvider.query.count() == 1
        assert providers_models.AllocineVenueProvider.query.count() == 1
        assert providers_models.AllocinePivot.query.count() == 1
        assert providers_models.Provider.query.count() > 0

    def test_delete_cascade_offerer_should_remove_related_bank_account(self):
        # Given
        bank_account = finance_factories.BankAccountFactory()
        offerer_to_delete = bank_account.offerer

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert offerers_models.Offerer.query.count() == 0
        assert finance_models.BankAccount.query.count() == 0


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

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_invitation_accepted")
    def test_send_offerer_attachment_invitation_accepted_email(
        self, mocked_send_offerer_attachment_invitation_accepted
    ):
        admin = users_factories.AdminFactory()
        invited_user = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=invited_user)
        offerer_invitation = offerers_factories.OffererInvitationFactory(
            offerer=user_offerer.offerer, email=invited_user.email
        )

        offerers_api.validate_offerer_attachment(user_offerer, admin)

        mocked_send_offerer_attachment_invitation_accepted.assert_called_once_with(
            invited_user, offerer_invitation.user.email
        )


class RejectOffererAttachementTest:
    def test_offerer_attachement_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        user_offerer_query = offerers_models.UserOfferer.query
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.REJECTED

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


class DeleteOffererAttachementTest:
    def test_offerer_attachement_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory()

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        user_offerer_query = offerers_models.UserOfferer.query
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.DELETED

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.NotValidatedUserOffererFactory(user=user, offerer=offerer)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        action = history_models.ActionHistory.query.one()
        assert action.actionType == history_models.ActionType.USER_OFFERER_DELETED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None


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
        assert user_offerer.offerer.dateValidated.strftime("%d/%m/%Y") == datetime.date.today().strftime("%d/%m/%Y")
        assert user_offerer.offerer.validationStatus == ValidationStatus.VALIDATED

    @patch("pcapi.core.search.async_index_offers_of_venue_ids")
    def test_offerer_is_validated_mail_sent(self, mocked_async_index_offers_of_venue_ids):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        venue1 = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer, adageId="11")
        mails = get_emails_by_venue(venue1)

        # When
        with patch("pcapi.core.mails.transactional.send_eac_offerer_activation_email") as mock_activation_mail:
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


class RejectOffererTest:
    def test_offerer_is_not_validated(self):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER)

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
        offerers_api.reject_offerer(
            user_offerer.offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER
        )

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer(
            user_offerer.offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER
        )

        # Then
        assert validated_user_offerer.user.has_pro_role
        assert not validated_user_offerer.user.has_non_attached_pro_role

    def test_attachment_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()

        # When
        offerers_api.reject_offerer(
            user_offerer.offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER
        )

        # Then
        user_offerer_query = offerers_models.UserOfferer.query
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.REJECTED

    def test_api_key_has_been_removed(self):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserNotValidatedOffererFactory()
        offerers_factories.ApiKeyFactory(offerer=user_offerer.offerer)

        # When
        offerers_api.reject_offerer(
            user_offerer.offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER
        )

        # Then
        user_offerer_query = offerers_models.UserOfferer.query
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.REJECTED
        assert offerers_models.ApiKey.query.count() == 0

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_rejection_email_to_pro")
    @patch("pcapi.core.mails.transactional.send_new_offerer_rejection_email_to_pro")
    def test_send_rejection_confirmation_email(
        self, send_new_offerer_rejection_email_to_pro, send_offerer_attachment_rejection_email_to_pro
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER)

        # Then
        send_new_offerer_rejection_email_to_pro.assert_called_once_with(offerer)
        send_offerer_attachment_rejection_email_to_pro.assert_not_called()  # one email is enough

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.NotValidatedOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.UserOffererFactory(
            offerer=offerer, validationStatus=ValidationStatus.NEW
        )  # another applicant

        # When
        offerers_api.reject_offerer(offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER)

        # Then
        action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.OFFERER_REJECTED
        ).one()
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

        action = history_models.ActionHistory.query.filter_by(
            actionType=history_models.ActionType.USER_OFFERER_REJECTED, user=user
        ).one()
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Compte pro rejeté suite au rejet de la structure"


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

    @time_machine.travel("2020-10-15 00:00:00", tick=False)
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

            mock_search_async_index_venue_ids.assert_called_once_with(
                [venue.id],
                reason=search.IndexationReason.VENUE_BANNER_UPDATE,
            )

    @time_machine.travel("2020-10-15 00:00:00", tick=False)
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

            mock_search_async_index_venue_ids.assert_called_once_with(
                [venue.id],
                reason=search.IndexationReason.VENUE_BANNER_UPDATE,
            )

    @patch("pcapi.core.search.async_index_venue_ids")
    def test_replace_venue_banner(self, mock_search_async_index_venue_ids, tmpdir):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        first_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        second_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_landscape.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        with override_settings(OBJECT_STORAGE_URL=tmpdir.dirname, LOCAL_STORAGE_DIR=pathlib.Path(tmpdir.dirname)):
            with time_machine.travel("2020-10-15 00:00:00"):
                offerers_api.save_venue_banner(user, venue, first_image_content, image_credit="first_image")

            with time_machine.travel("2020-10-15 00:00:05"):
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
            with time_machine.travel("2020-10-15 00:00:00"):
                offerers_api.save_venue_banner(user, venue, first_image_content, image_credit="first_image")
                move_venue_banner_to_legacy_location(venue, directory, "1602720000")
            with time_machine.travel("2020-10-15 00:00:01"):
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
            venues = list(offerers_api.get_venues_by_batch())

        assert {venue.id for venue in venues} == {venue.id for venue in eligible_venues}

    def test_max_limit_number_of_venues(self) -> None:
        eligible_venues = offerers_factories.VenueFactory.create_batch(3, isPermanent=True)

        with assert_num_queries(1):
            venues = list(offerers_api.get_venues_by_batch(max_venues=1))

        assert venues[0].id in {venue.id for venue in eligible_venues}


class LinkVenueToPricingPointTest:
    def test_no_pre_existing_link(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        assert offerers_models.VenuePricingPointLink.query.count() == 0

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)

        db.session.rollback()  # ensure that commit() was called before assertions

        new_link = offerers_models.VenuePricingPointLink.query.one()
        assert new_link.venue == venue
        assert new_link.pricingPoint == pricing_point
        assert new_link.timespan.upper is None

    def test_populate_finance_event_pricing_point_id(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        event = finance_factories.UsedBookingFinanceEventFactory(booking=booking)
        assert event.pricingPointId is None

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)
        assert event.pricingPoint == pricing_point
        assert event.status == finance_models.FinanceEventStatus.READY

    def test_behaviour_if_pre_existing_link(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        pricing_point_1 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        offerers_factories.VenuePricingPointLinkFactory(venue=venue, pricingPoint=pricing_point_1)
        pre_existing_link = offerers_models.VenuePricingPointLink.query.one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with pytest.raises(offerers_exceptions.CannotLinkVenueToPricingPoint):
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id)
        assert offerers_models.VenuePricingPointLink.query.one() == pre_existing_link

        # Now force the link.
        offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id, force_link=True)
        link = offerers_models.VenuePricingPointLink.query.order_by(
            offerers_models.VenuePricingPointLink.id.desc()
        ).first()
        assert link.venue == venue
        assert link.pricingPoint == pricing_point_2

    def test_fails_if_venue_has_siret(self):
        pricing_point = offerers_factories.VenueFactory()
        offerer = pricing_point.managingOfferer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="1234")

        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)
        msg = "Ce lieu a un SIRET, vous ne pouvez donc pas choisir un autre lieu pour le calcul du barème de remboursement."
        assert error.value.errors == {"pricingPointId": [msg]}

    def test_no_commit(self):
        venue = offerers_factories.VenueWithoutSiretFactory()
        pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id, commit=False)

        db.session.rollback()  # test after commit() is not called

        assert offerers_models.VenuePricingPointLink.query.count() == 0


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


class GetOffererTotalRevenueTest:
    def _create_data(self):
        offerer = offerers_factories.OffererFactory()
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer, stock__price=10)
        bookings_factories.UsedBookingFactory(
            stock__offer__venue__managingOfferer=offerer,
            stock__price=11.5,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=400),
        )
        bookings_factories.ReimbursedBookingFactory(
            stock__offer__venue__managingOfferer=offerer, stock__price=12, quantity=2
        )
        bookings_factories.CancelledBookingFactory(stock__offer__venue__managingOfferer=offerer, stock__price=120)
        educational_factories.PendingCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer, collectiveStock__price=1333
        )
        educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer, collectiveStock__price=1444
        )
        educational_factories.ReimbursedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__price=1555,
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=500),
        )
        educational_factories.CancelledCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer, collectiveStock__price=6000
        )
        bookings_factories.UsedBookingFactory(stock__price=180)  # ignored
        educational_factories.UsedCollectiveBookingFactory(collectiveStock__price=7000)  # ignored
        return offerer

    def test_revenue_all_years(self):
        offerer = self._create_data()
        total_revenue = offerers_api.get_offerer_total_revenue(offerer.id)
        assert float(total_revenue) == 10.0 + 11.50 + 12 * 2 + 1333 + 1444 + 1555

    def test_revenue_only_current_year(self):
        offerer = self._create_data()
        total_revenue = offerers_api.get_offerer_total_revenue(offerer.id, only_current_year=True)
        assert float(total_revenue) == 10.0 + 12 * 2 + 1333 + 1444


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
        assert stats == {"DELETED": 0, "NEW": 1, "PENDING": 2, "VALIDATED": 3, "REJECTED": 4}

    def test_get_offerer_stats_zero(self, client):
        # when
        with assert_num_queries(1):
            stats = offerers_api.count_offerers_by_validation_status()

        # then
        assert stats == {"DELETED": 0, "NEW": 0, "PENDING": 0, "VALIDATED": 0, "REJECTED": 0}


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
        assert venue.street == "3 RUE DE VALOIS"
        assert venue.banId == "75101_9575_00003"
        assert venue.bookingEmail == "pro@example.com"
        assert venue.city == "Paris"
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

    def assert_venue_registration_attrs(self, venue: Venue) -> None:
        assert offerers_models.VenueRegistration.query.all() == [venue.registration]
        assert venue.registration.target == offerers_models.Target.INDIVIDUAL
        assert (
            venue.registration.webPresence
            == "https://www.example.com, https://instagram.com/example, https://mastodon.social/@example"
        )

    def assert_only_welcome_email_to_pro_was_sent(self) -> None:
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"]["id_not_prod"] == TransactionalEmail.WELCOME_TO_PRO.value.id

    def get_onboarding_data(
        self, create_venue_without_siret: bool
    ) -> offerers_serialize.SaveNewOnboardingDataQueryModel:
        return offerers_serialize.SaveNewOnboardingDataQueryModel(
            banId="75101_9575_00003",
            city="Paris",
            createVenueWithoutSiret=create_venue_without_siret,
            latitude=2.30829,
            longitude=48.87171,
            postalCode="75001",
            publicName="Nom public de mon lieu",
            siret="85331845900031",
            street="3 RUE DE VALOIS",
            target=offerers_models.Target.INDIVIDUAL,
            venueTypeCode=offerers_models.VenueTypeCode.MOVIE.name,
            webPresence="https://www.example.com, https://instagram.com/example, https://mastodon.social/@example",
            token="token",
        )

    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=True)
    def test_new_siren_new_siret(self, requests_mock):
        api_adresse_response = {
            "type": "FeatureCollection",
            "version": "draft",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [2.337933, 48.863666]},
                    "properties": {
                        "label": "3 Rue de Valois 75001 Paris",
                        "score": 0.9652045454545454,
                        "housenumber": "3",
                        "id": "75101_9575_00003",
                        "name": "3 Rue de Valois",
                        "postcode": "75001",
                        "citycode": "75101",
                        "x": 651428.82,
                        "y": 6862829.62,
                        "city": "Paris",
                        "district": "Paris 1er Arrondissement",
                        "context": "75, Paris, Île-de-France",
                        "type": "housenumber",
                        "importance": 0.61725,
                        "street": "Rue de Valois",
                    },
                }
            ],
            "attribution": "BAN",
            "licence": "ETALAB-2.0",
            "query": "3 Rue de valois, 75001 Paris",
            "filters": {"postcode": "75001"},
            "limit": 1,
        }
        requests_mock.get(
            "https://api-adresse.data.gouv.fr/search?q=3 RUE DE VALOIS&postcode=75001&autocomplete=0&limit=1",
            json=api_adresse_response,
        )
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        address = geography_models.Address.query.one()
        offerer_address = offerers_models.OffererAddress.query.one()

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.street == "3 RUE DE VALOIS"
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
        assert created_venue.street.lower() == address.street.lower()
        assert created_venue.city == address.city
        assert created_venue.postalCode == address.postalCode
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.departmentCode == "75"
        assert address.timezone == "Europe/Paris"
        assert created_venue.offererAddressId == offerer_address.id
        assert offerer_address.addressId == address.id

        # Action logs
        assert history_models.ActionHistory.query.count() == 2
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.OFFERER_NEW
        ).one()
        assert offerer_action.offerer == created_offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        venue_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED
        ).one()
        assert venue_action.venue == created_venue
        assert venue_action.authorUser == user

        self.assert_only_welcome_email_to_pro_was_sent()
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

    @override_features(ENABLE_ADDRESS_WRITING_WHILE_CREATING_UPDATING_VENUE=False)
    def test_new_siren_new_siret_without_double_model_writing(self, requests_mock):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        assert not geography_models.Address.query.one_or_none()
        assert not offerers_models.OffererAddress.query.one_or_none()

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.street == "3 RUE DE VALOIS"
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
        assert not created_venue.offererAddressId

        # Action logs (content already checked in test_new_siren_new_siret)
        assert history_models.ActionHistory.query.count() == 2

        self.assert_only_welcome_email_to_pro_was_sent()
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

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
        assert history_models.ActionHistory.query.count() == 2
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW
        ).one()
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        venue_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED
        ).one()
        assert venue_action.venue == created_venue
        assert venue_action.authorUser == user

        assert len(mails_testing.outbox) == 0
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

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
        assert history_models.ActionHistory.query.count() == 2
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW
        ).one()
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        offerer_action = history_models.ActionHistory.query.filter(
            history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED
        ).one()
        assert offerer_action.venue == created_venue
        assert offerer_action.authorUser == user

        assert len(mails_testing.outbox) == 0
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

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
        assert len(mails_testing.outbox) == 0
        # Venue Registration
        assert offerers_models.VenueRegistration.query.count() == 0

    def test_missing_address(self):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()
        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.street = None

        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.street is None
        assert created_offerer.city == "Paris"
        assert created_offerer.postalCode == "75001"
        # 1 virtual Venue + 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 2
        created_venue, _ = sorted(created_user_offerer.offerer.managedVenues, key=lambda v: v.isVirtual)
        assert created_venue.street == "n/d"
        assert created_venue.city == "Paris"
        assert created_venue.latitude == decimal.Decimal("2.30829")
        assert created_venue.longitude == decimal.Decimal("48.87171")
        assert created_venue.postalCode == "75001"

    def test_missing_ban_id(self):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()
        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.banId = None

        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.street == "3 RUE DE VALOIS"
        assert created_offerer.city == "Paris"
        assert created_offerer.postalCode == "75001"
        # 1 virtual Venue + 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 2
        created_venue, _ = sorted(created_user_offerer.offerer.managedVenues, key=lambda v: v.isVirtual)
        assert created_venue.street == "3 RUE DE VALOIS"
        assert created_venue.banId is None
        assert created_venue.city == "Paris"
        assert created_venue.latitude == decimal.Decimal("2.30829")
        assert created_venue.longitude == decimal.Decimal("48.87171")
        assert created_venue.postalCode == "75001"

    @patch("pcapi.connectors.virustotal.request_url_scan")
    def test_web_presence_url_scanned(self, mock_request_url_scan):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        offerers_api.create_from_onboarding_data(user, onboarding_data)

        mock_request_url_scan.assert_called()
        assert mock_request_url_scan.call_count == 3
        assert {item[0][0] for item in mock_request_url_scan.call_args_list} == {
            "https://www.example.com",
            "https://instagram.com/example",
            "https://mastodon.social/@example",
        }


class InviteMembersTest:
    def test_offerer_invitation_created_when_invite_new_user(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        offerers_api.invite_member(offerer=offerer, email="new.user@example.com", current_user=pro_user)

        offerer_invitation = offerers_models.OffererInvitation.query.one()
        assert offerer_invitation.email == "new.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.PENDING
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value.id
        )

        assert history_models.ActionHistory.query.count() == 0

    def test_offerer_invitation_created_when_user_exists_and_email_not_validated(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        users_factories.UserFactory(email="new.user@example.com", isEmailValidated=False)

        offerers_api.invite_member(offerer=offerer, email="new.user@example.com", current_user=pro_user)

        offerer_invitation = offerers_models.OffererInvitation.query.one()
        assert offerer_invitation.email == "new.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.PENDING
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value.id
        )

        assert history_models.ActionHistory.query.count() == 0

    def test_raise_and_not_create_offerer_invitation_when_invitation_already_exists(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(user=pro_user, offerer=offerer, email="new.user@example.com")

        with pytest.raises(offerers_exceptions.EmailAlreadyInvitedException) as exception:
            offerers_api.invite_member(offerer=offerer, email="new.user@example.com", current_user=pro_user)

        assert exception.value.errors["EmailAlreadyInvitedException"] == [
            "Une invitation a déjà été envoyée à ce collaborateur"
        ]
        offerer_invitations = offerers_models.OffererInvitation.query.all()
        assert len(offerer_invitations) == 1
        assert len(mails_testing.outbox) == 0

        assert history_models.ActionHistory.query.count() == 0

    def test_raise_error_not_create_offerer_invitation_when_user_already_attached_to_offerer(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        attached_user = users_factories.ProFactory(email="attached.user@example.com")
        offerers_factories.UserOffererFactory(user=attached_user, offerer=offerer)

        with pytest.raises(offerers_exceptions.UserAlreadyAttachedToOffererException) as exception:
            offerers_api.invite_member(offerer=offerer, email="attached.user@example.com", current_user=pro_user)

        assert exception.value.errors["UserAlreadyAttachedToOffererException"] == [
            "Ce collaborateur est déjà membre de votre structure"
        ]
        offerer_invitations = offerers_models.OffererInvitation.query.all()
        assert len(offerer_invitations) == 0
        assert len(mails_testing.outbox) == 0

        assert history_models.ActionHistory.query.count() == 0

    def test_user_offerer_created_when_user_exists_and_attached_to_another_offerer(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        attached_to_other_offerer_user = users_factories.ProFactory(email="attached.user@example.com")
        offerers_factories.UserOffererFactory(user=attached_to_other_offerer_user)

        offerers_api.invite_member(offerer=offerer, email="attached.user@example.com", current_user=pro_user)

        offerer_invitation = offerers_models.OffererInvitation.query.one()
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value.id
        )
        user_offerer = offerers_models.UserOfferer.query.filter_by(
            userId=attached_to_other_offerer_user.id, offererId=offerer.id
        ).one()
        assert user_offerer.validationStatus == ValidationStatus.NEW
        assert offerer_invitation.email == "attached.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.ACCEPTED

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == pro_user
        assert actions_list[0].user == attached_to_other_offerer_user
        assert actions_list[0].comment == "Rattachement créé par invitation"
        assert actions_list[0].offerer == offerer
        assert actions_list[0].extraData == {
            "inviter_user_id": pro_user.id,
            "offerer_invitation_id": offerer_invitation.id,
        }


class AcceptOffererInvitationTest:
    def test_accept_offerer_invitation_when_invitation_exist(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(offerer=offerer, user=pro_user, email="new.user@example.com")
        user = users_factories.UserFactory(email="new.user@example.com")

        offerers_api.accept_offerer_invitation_if_exists(user)

        new_user_offerer = offerers_models.UserOfferer.query.filter_by(validationStatus=ValidationStatus.NEW).one()
        offerer_invitation = offerers_models.OffererInvitation.query.one()

        assert new_user_offerer.offererId == offerer.id
        assert new_user_offerer.userId == user.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.ACCEPTED

        actions_list = history_models.ActionHistory.query.all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].comment == "Rattachement créé par invitation"
        assert actions_list[0].offerer == offerer
        assert actions_list[0].extraData == {
            "inviter_user_id": pro_user.id,
            "offerer_invitation_id": offerer_invitation.id,
        }

    def test_do_not_recreate_new_user_offerer_if_invitation_already_accepted(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(
            offerer=offerer,
            user=pro_user,
            email="new.user@example.com",
            status=offerers_models.InvitationStatus.ACCEPTED,
        )
        user = users_factories.UserFactory(email="new.user@example.com")
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)

        offerers_api.accept_offerer_invitation_if_exists(user)

        user_offerers = offerers_models.UserOfferer.query.all()

        assert len(user_offerers) == 2
        assert history_models.ActionHistory.query.count() == 0


class OpeningHoursTest:
    def test_opening_hours_timespan_must_be_maximum_two(self):
        timespan_list = timespan_str_to_numrange([("10:00", "13:00"), ("14:00", "19:00"), ("23:30", "5:00")])
        opening_hours = offerers_models.OpeningHours(weekday=offerers_models.Weekday.SATURDAY)
        with pytest.raises(ValueError):
            offerers_api.add_timespan(opening_hours, timespan_list[0])
            offerers_api.add_timespan(opening_hours, timespan_list[1])
            offerers_api.add_timespan(opening_hours, timespan_list[2])

    def test_opening_hours_timespan_overlapping(self):
        timespan_list = timespan_str_to_numrange([("10:00", "14:00"), ("13:00", "19:00")])
        opening_hours = offerers_models.OpeningHours(weekday=offerers_models.Weekday.SATURDAY)
        with pytest.raises(ValueError):
            offerers_api.add_timespan(opening_hours, timespan_list[0])
            offerers_api.add_timespan(opening_hours, timespan_list[1])

    def test_add_opening_hours_timespan_is_sorted_chronogicaly(self):
        timespan_list = timespan_str_to_numrange([("10:00", "13:00"), ("14:00", "19:00")])
        opening_hours = offerers_models.OpeningHours(weekday=offerers_models.Weekday.SATURDAY)
        offerers_api.add_timespan(opening_hours, timespan_list[1])
        offerers_api.add_timespan(opening_hours, timespan_list[0])
        assert opening_hours.timespan[0] == timespan_list[0]
        assert opening_hours.timespan[1] == timespan_list[1]


class AccessibilityProviderTest:
    def test_set_accessibility_provider_id(self):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        venue_accessibility = offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerers_api.set_accessibility_provider_id(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == venue_accessibility.externalAccessibilityId

    def test_set_accessibility_last_update_at_provider_id(self):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerers_api.set_accessibility_infos_from_provider_id(venue)
        assert venue.accessibilityProvider.lastUpdateAtProvider == datetime.datetime(2024, 3, 1, 0, 0)

    def test_set_accessibility_infos_from_provider_id(self):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerers_api.set_accessibility_infos_from_provider_id(venue)
        assert venue.accessibilityProvider.externalAccessibilityData["access_modality"] == [
            acceslibre_connector.ExpectedFieldsEnum.EXTERIOR_ONE_LEVEL,
            acceslibre_connector.ExpectedFieldsEnum.ENTRANCE_ONE_LEVEL,
        ]

    def test_synchronize_accessibility_provider_no_data(self):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        accessibility_provider = offerers_factories.AccessibilityProviderFactory(
            venue=venue, externalAccessibilityData=None
        )
        offerers_api.synchronize_accessibility_provider(venue)
        assert accessibility_provider.externalAccessibilityData is not None

    def test_synchronize_accessibility_provider_with_new_update(self):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        accessibility_provider = offerers_factories.AccessibilityProviderFactory(
            venue=venue, lastUpdateAtProvider=datetime.datetime(2023, 2, 1)
        )
        # TestingBackend for acceslibre get_id_at_accessibility_provider returns datetime(2024, 3, 1, 0, 0)
        accessibility_provider.externalAccessibilityData["audio_description"] = (
            acceslibre_connector.ExpectedFieldsEnum.AUDIODESCRIPTION_NO_DEVICE
        )

        # Synchronize should happen as provider last update is more recent than accessibility_provider.lastUpdateAtProvider
        offerers_api.synchronize_accessibility_provider(venue)
        assert accessibility_provider.externalAccessibilityData["audio_description"] == [
            acceslibre_connector.ExpectedFieldsEnum.AUDIODESCRIPTION_OCCASIONAL
        ]

    @patch("pcapi.connectors.acceslibre.get_accessibility_infos")
    @patch("pcapi.connectors.acceslibre.get_id_at_accessibility_provider")
    def test_synchronize_accessibility_provider_with_new_slug(
        self, mock_get_id_at_accessibility_provider, mock_get_accessibility_infos
    ):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            postalCode="75001",
            city="Paris",
        )
        mock_get_id_at_accessibility_provider.side_effect = [
            acceslibre_connector.AcceslibreInfos(slug="nouveau-slug", url="https://nouvelle.adresse/nouveau-slug")
        ]
        # While trying to synchronize venue with acceslibre, we receive None when fetching widget data
        # This means the entry with this slug (ie. externalAccessibilityId) has been removed
        # from acceslibre database (usualy because of deduplication);
        # In that case, we try a new match and look for the new slug
        mock_get_accessibility_infos.side_effect = [
            (None, None),
            (datetime.datetime(2024, 3, 1, 0, 0), acceslibre_connector.AccessibilityInfo()),
        ]

        accessibility_provider = offerers_factories.AccessibilityProviderFactory(
            venue=venue, externalAccessibilityId="slug-qui-n-existe-plus"
        )
        offerers_api.synchronize_accessibility_provider(venue, force_sync=True)
        assert accessibility_provider.externalAccessibilityId == "nouveau-slug"
        assert accessibility_provider.externalAccessibilityUrl == "https://nouvelle.adresse/nouveau-slug"

    def test_count_venues_with_accessibility_provider(self):
        offerers_factories.VenueFactory.create_batch(3, isPermanent=True, isVirtual=False)
        venue = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        count = offerers_api.count_permanent_venues_with_accessibility_provider()
        assert count == 1

    def test_get_permanent_venues_with_accessibility_provider(self):
        offerers_factories.VenueFactory.create_batch(3, isPermanent=True, isVirtual=False)
        venue = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        venues_list = offerers_api.get_permanent_venues_with_accessibility_provider(batch_size=10, batch_num=0)
        assert len(venues_list) == 1
        assert venues_list[0] == venue

    def test_get_permanent_venues_without_accessibility_provider(self):
        offerers_factories.VenueFactory.create_batch(3, isPermanent=True, isVirtual=False)
        venue = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        venues_list = offerers_api.get_permanent_venues_without_accessibility_provider()
        assert len(venues_list) == 3

    @patch("pcapi.connectors.acceslibre.find_new_entries_by_activity")
    def test_match_venue_with_new_entries(self, mock_find_new_entries_by_activity):
        # returns mock results from acceslibre TestingBackend connector
        mock_find_new_entries_by_activity.side_effect = [
            [
                acceslibre_connector.AcceslibreResult(
                    slug="mon-lieu-chez-acceslibre",
                    web_url="https://une-fausse-url.com",
                    nom="Un lieu",
                    adresse="3 Rue de Valois 75001 Paris",
                    code_postal="75001",
                    commune="Paris",
                    ban_id="75001_1234_abcde",
                    activite={"nom": "Bibliothèque Médiathèque", "slug": "bibliotheque-mediatheque"},
                    siret="",
                ),
                acceslibre_connector.AcceslibreResult(
                    slug="mon-autre-lieu-chez-acceslibre",
                    web_url="https://une-autre-fausse-url.com",
                    nom="Un autre lieu",
                    adresse="5 rue ailleurs 75013 Paris",
                    code_postal="75001",
                    commune="Paris",
                    ban_id="75001_1234_abcdf",
                    activite={"nom": "Bibliothèque Médiathèque", "slug": "bibliotheque-mediatheque"},
                    siret="",
                ),
            ],
        ]

        results_by_activity = acceslibre_connector.find_new_entries_by_activity(
            activity=acceslibre_connector.AcceslibreActivity.BIBLIOTHEQUE,
        )

        venues_list = [offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)]
        venue = offerers_factories.VenueFactory(
            isPermanent=True,
            isVirtual=False,
            name="Un lieu",
            postalCode="75001",
            city="Paris",
            street="3 Rue de Valois",
        )
        venues_list.append(venue)

        offerers_api.match_venue_with_new_entries(venues_list, results_by_activity)
        assert venue.external_accessibility_url == "https://une-fausse-url.com"
        assert venue.external_accessibility_id == "mon-lieu-chez-acceslibre"

    def test_acceslibre_matching(self):
        venues_list = [offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)]
        venue = offerers_factories.VenueFactory(
            isPermanent=True,
            isVirtual=False,
            name="Un lieu",
            postalCode="75001",
            city="Paris",
            street="3 Rue de Valois",
        )
        venues_list.append(venue)

        # match result is given by find_new_entries_by_activity in TestingBackend class in acceslibre connector
        offerers_api.acceslibre_matching(batch_size=1000, dry_run=False, start_from_batch=1)

        assert (
            venue.external_accessibility_url == "https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/"
        )
        assert venue.external_accessibility_id == "mon-lieu-chez-acceslibre"

    @patch("pcapi.connectors.acceslibre.get_id_at_accessibility_provider")
    def test_synchronize_venues_with_acceslibre(self, mock_get_id_at_accessibility_provider):
        mock_get_id_at_accessibility_provider.side_effect = [
            None,
            acceslibre_connector.AcceslibreInfos(slug="mon-slug", url="https://mon.adresse/mon-slug"),
        ]

        venue_1 = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)
        venue_2 = offerers_factories.VenueFactory(isPermanent=True, isVirtual=False)
        venue_ids = [venue_1.id, venue_2.id]

        # match result is given by find_new_entries_by_activity in TestingBackend class in acceslibre connector
        offerers_api.synchronize_venues_with_acceslibre(venue_ids, dry_run=False)

        assert not venue_1.accessibilityProvider
        assert venue_2.external_accessibility_url == "https://mon.adresse/mon-slug"
        assert venue_2.external_accessibility_id == "mon-slug"


class GetOffererConfidenceLevelTest:
    def test_no_rule(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.ManualReviewOffererConfidenceRuleFactory()
        offerers_factories.WhitelistedVenueConfidenceRuleFactory()

        confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level is None

    def test_offerer_manual_review(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.ManualReviewOffererConfidenceRuleFactory(offerer=venue.managingOfferer)
        offerers_factories.WhitelistedVenueConfidenceRuleFactory()

        confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW

    def test_offerer_whitelist(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.WhitelistedOffererConfidenceRuleFactory(offerer=venue.managingOfferer)
        offerers_factories.ManualReviewVenueConfidenceRuleFactory()

        confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level == offerers_models.OffererConfidenceLevel.WHITELIST

    def test_venue_manual_review(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue=venue)
        offerers_factories.WhitelistedOffererConfidenceRuleFactory()

        confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level == offerers_models.OffererConfidenceLevel.MANUAL_REVIEW

    def test_venue_whitelist(self):
        venue = offerers_factories.VenueFactory()
        offerers_factories.WhitelistedVenueConfidenceRuleFactory(venue=venue)
        offerers_factories.ManualReviewOffererConfidenceRuleFactory()

        confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level == offerers_models.OffererConfidenceLevel.WHITELIST

    def test_conflict(self, caplog):
        venue = offerers_factories.VenueFactory()
        offerers_factories.WhitelistedOffererConfidenceRuleFactory(offerer=venue.managingOfferer)
        offerers_factories.ManualReviewVenueConfidenceRuleFactory(venue=venue)

        with caplog.at_level(logging.ERROR):
            confidence_level = offerers_api.get_offer_confidence_level(venue)

        assert confidence_level == offerers_models.OffererConfidenceLevel.WHITELIST  # offerer first

        assert caplog.records[0].message == "Incompatible offerer rule detected"
        assert caplog.records[0].extra == {"offerer_id": venue.managingOffererId, "venue_id": venue.id}


class GetOffererAddressTest:
    @pytest.mark.parametrize("same_label,same_address", [[True, False], [False, True], [True, True], [False, False]])
    def test_get_or_create_offerer_address(self, same_label, same_address):
        offerer = offerers_factories.OffererFactory()
        oa_1 = offerers_factories.OffererAddressFactory(offerer=offerer)
        other_addresss = geography_factories.AddressFactory(
            street="1 rue de la paix",
        )

        oa_return = offerers_api.get_or_create_offerer_address(
            offerer_id=offerer.id,
            address_id=oa_1.address.id if same_address else other_addresss.id,
            label=oa_1.label if same_label else "somethingdifferent",
        )
        if same_label and same_address:
            assert oa_return == oa_1
        else:
            assert oa_return.offerer == offerer
            assert oa_return != oa_1

    @pytest.mark.parametrize("existant_address", [True, False])
    def test_get_or_create_address(self, existant_address):
        if existant_address:
            old_address = geography_factories.AddressFactory(
                street="1 rue de la paix",
                city="Paris",
                postalCode="75103",
                latitude=40.8566,
                longitude=1.3522,
                banId="75103_7560_00001",
            )
        location_data = offerers_api.LocationData(
            street="1 rue de la paix",
            city="Paris",
            postal_code="75103",
            latitude=40.8566,
            longitude=1.3522,
            insee_code="75103",
            ban_id="75103_7560_00001",
        )
        address = offerers_api.get_or_create_address(location_data=location_data, is_manual_edition=False)
        assert len(geography_models.Address.query.all()) == 1
        if existant_address:
            assert address == old_address
        else:
            assert address.street == "1 rue de la paix"
            assert address.city == "Paris"
            assert address.postalCode == "75103"
            assert address.latitude == 40.8566
            assert address.longitude == 1.3522
