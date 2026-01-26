import dataclasses
import datetime
import decimal
import logging
import os
import pathlib
from unittest.mock import patch

import pytest
import sqlalchemy as sa
import time_machine

import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.exceptions as offerers_exceptions
from pcapi.connectors import acceslibre as acceslibre_connector
from pcapi.connectors.entreprise import models as sirene_models
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
from pcapi.core.history import factories as history_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.repository import get_emails_by_venue
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.opening_hours import schemas as opening_hours_schemas
from pcapi.core.providers import factories as providers_factories
from pcapi.core.providers import models as providers_models
from pcapi.core.search.models import IndexationReason
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import api_errors
from pcapi.models import db
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.routes.serialization import offerers_serialize
from pcapi.routes.serialization import venues_serialize
from pcapi.utils import date as date_utils
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
    db.session.refresh(offerer)
    assert expected_tag in (tag.label for tag in offerer.tags)


class UpdateVenueTest:
    def test_update_venue_switch_addresses_twice(self):
        """
        This test ensures that we do no longer have the exception:
        psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "ix_unique_offerer_address_per_label"
        DETAIL:  Key ("offererId", "addressId", label)=(811, 512, Le Petit Rintintin 0) already exists.
        """
        venue = offerers_factories.VenueFactory(
            offererAddress__address__street="Place de la Concorde",
            offererAddress__address__postalCode="75001",
            offererAddress__address__latitude="48.865609",
            offererAddress__address__longitude="2.322913",
            offererAddress__address__banId="75101_2259",
        )
        author = users_factories.UserFactory()

        modifications_1 = {
            "street": "Avenue des Champs Elysées",
            "latitude": "48.871285",
            "longitude": "2.302859",
            "banId": "75108_1733",
        }
        modifications_2 = {
            "street": "Place de la Concorde",
            "postalCode": "75001",
            "latitude": "48.865609",
            "longitude": "2.322913",
            "banId": "75101_2259",
        }

        offerers_api.update_venue(venue, {}, modifications_1, author)
        offerer_address = venue.offererAddress
        assert offerer_address.label is None
        assert offerer_address.type == offerers_models.LocationType.VENUE_LOCATION
        assert offerer_address.venue == venue
        address_1 = offerer_address.address
        assert address_1.street == modifications_1["street"]

        offerers_api.update_venue(venue, {}, modifications_2, author)
        assert venue.offererAddress == offerer_address  # same object updated
        assert offerer_address.id == offerer_address.id
        assert offerer_address.label is None
        assert offerer_address.type == offerers_models.LocationType.VENUE_LOCATION
        assert offerer_address.venue == venue
        address_2 = offerer_address.address
        assert address_2.id != address_1.id
        assert address_2.street == modifications_2["street"]

        offerers_api.update_venue(venue, {}, modifications_1, author)
        assert venue.offererAddress == offerer_address  # same object updated
        assert venue.offererAddress.address == address_1

    def test_add_new_opening_hours_to_venue(self):
        venue = offerers_factories.VenueFactory()
        author = users_factories.UserFactory()

        new_opening_hours = opening_hours_schemas.WeekdayOpeningHoursTimespans(MONDAY=[["10:00", "18:00"]])
        offerers_api.update_venue(venue, {}, {}, author, opening_hours=new_opening_hours)

        opening_hours = db.session.query(offerers_models.OpeningHours).filter_by(venueId=venue.id).all()
        assert len(opening_hours) == 1

        opening_hours = opening_hours[0]
        assert opening_hours.weekday.value == "MONDAY"

        assert len(opening_hours.timespan) == 1
        assert opening_hours.timespan[0].lower == 10 * 60
        assert opening_hours.timespan[0].upper == 18 * 60

    @patch("pcapi.workers.match_acceslibre_job.match_acceslibre_job")
    def test_changing_address_should_not_synchronize_when_closed_to_public(self, mock_match_acceslibre_job):
        venue = offerers_factories.VenueFactory(isOpenToPublic=False, isPermanent=True)
        author = users_factories.UserFactory()
        modifications = {
            "street": "Avenue des Champs Elysées",
            "latitude": "48.871285",
            "longitude": "2.302859",
            "banId": "75108_1733",
        }
        offerers_api.update_venue(venue, {}, modifications, author)

        mock_match_acceslibre_job.assert_not_called()


class CreateVenueTest:
    def base_data(self, offerer):
        return {
            "address": {
                "street": "rue du test",
                "city": "Paris",
                "postalCode": "75002",
                "banId": "75113_1834_00007",
                "latitude": 1,
                "longitude": 2,
            },
            "managingOffererId": offerer.id,
            "name": "La Venue",
            "activity": "CINEMA",
            "bookingEmail": "venue@example.com",
            "siret": offerer.siren + "00000",
            "isOpenToPublic": False,
            "audioDisabilityCompliant": True,
            "mentalDisabilityCompliant": True,
            "motorDisabilityCompliant": True,
            "visualDisabilityCompliant": True,
        }

    def test_basics(self):
        user_offerer = offerers_factories.UserOffererFactory()
        data = venues_serialize.PostVenueBodyModel(**self.base_data(user_offerer.offerer))
        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.managingOfferer == user_offerer.offerer
        assert venue.name == "La Venue"
        assert venue.publicName == "La Venue"  # empty/non public name copies name
        assert venue.bookingEmail == "venue@example.com"
        assert venue.dmsToken
        assert venue.current_pricing_point_id == venue.id

        offerer_address = db.session.query(offerers_models.OffererAddress).one()
        assert offerer_address.label is None
        assert offerer_address.offerer == user_offerer.offerer
        assert offerer_address.type == offerers_models.LocationType.VENUE_LOCATION
        assert offerer_address.venue == venue
        assert offerer_address.address.banId == "75113_1834_00007"
        assert offerer_address.address.street == "rue du test"
        assert offerer_address.address.postalCode == "75002"
        assert offerer_address.address.city == "Paris"
        assert offerer_address.address.latitude == 1
        assert offerer_address.address.longitude == 2
        assert offerer_address.address.departmentCode == "75"
        assert offerer_address.address.timezone == "Europe/Paris"
        assert offerer_address.address.isManualEdition is False
        assert venue.offererAddress == offerer_address

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.VENUE_CREATED
        assert action.authorUser == user_offerer.user
        assert action.user is None
        assert action.offerer is None
        assert action.venue == venue

    def test_venue_is_permanent_when_created_with_siret(self):
        user_offerer = offerers_factories.UserOffererFactory()
        data = venues_serialize.PostVenueBodyModel(**self.base_data(user_offerer.offerer))
        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.isPermanent is True

    def test_venue_is_permanent_when_created_open_to_public(self):
        user_offerer = offerers_factories.UserOffererFactory()
        init_data = self.base_data(user_offerer.offerer) | {
            "siret": None,
            "comment": "no siret",
            "isOpenToPublic": True,
        }
        data = venues_serialize.PostVenueBodyModel(**init_data)
        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.isPermanent is True

    def test_venue_is_permanent_when_created_with_siret_and_open_to_public(self):
        user_offerer = offerers_factories.UserOffererFactory()
        init_data = self.base_data(user_offerer.offerer) | {"isOpenToPublic": True}
        data = venues_serialize.PostVenueBodyModel(**init_data)
        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.isPermanent is True

    def test_create_venue_closed_to_public_should_be_permanent(self):
        user_offerer = offerers_factories.UserOffererFactory()
        init_data = self.base_data(user_offerer.offerer) | {
            "isOpenToPublic": False,
        }
        data = venues_serialize.PostVenueBodyModel(**init_data)
        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.isPermanent is True

    def test_venue_with_no_siret_has_no_pricing_point(self):
        user_offerer = offerers_factories.UserOffererFactory()
        data = self.base_data(user_offerer.offerer) | {"siret": None, "comment": "no siret"}
        data = venues_serialize.PostVenueBodyModel(**data)

        offerers_api.create_venue(data, user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.siret is None
        assert venue.current_pricing_point_id is None

    @pytest.mark.parametrize(
        "cultural_domains,activity,expected_activity_code",
        (
            (("Architecture",), offerers_models.Activity.ART_GALLERY, offerers_models.Activity.ART_GALLERY),
            (("Architecture",), None, None),
            (("Média et information", "Bande dessinée"), None, None),
        ),
    )
    def test_venue_with_cultural_domains(self, cultural_domains, activity, expected_activity_code):
        user_offerer = offerers_factories.UserOffererFactory()
        for domain_name in ["Architecture", "Média et information", "Bande dessinée", "Musique"]:
            educational_factories.EducationalDomainFactory(name=domain_name)
        data = self.base_data(user_offerer.offerer) | {"culturalDomains": cultural_domains}
        if activity:
            data["activity"] = activity.name
        else:
            del data["activity"]
        offerers_api.create_venue(venues_serialize.PostVenueBodyModel(**data), user_offerer.user)

        venue = db.session.query(offerers_models.Venue).one()
        assert venue.activity == expected_activity_code
        assert {domain.name for domain in venue.collectiveDomains} == set(cultural_domains)


class DeleteVenueTest:
    def test_delete_venue_should_abort_when_venue_has_any_bookings(self):
        booking = bookings_factories.BookingFactory()
        venue_to_delete = booking.venue

        with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
            "Partenaire culturel non supprimable car il contient des réservations"
        ]
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Stock).count() == 1
        assert db.session.query(bookings_models.Booking).count() == 1

    def test_delete_venue_should_abort_when_venue_has_any_collective_bookings(self):
        booking = educational_factories.CollectiveBookingFactory()
        venue_to_delete = booking.venue

        with pytest.raises(offerers_exceptions.CannotDeleteVenueWithBookingsException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        assert exception.value.errors["cannotDeleteVenueWithBookingsException"] == [
            "Partenaire culturel non supprimable car il contient des réservations"
        ]
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(educational_models.CollectiveStock).count() == 1
        assert db.session.query(educational_models.CollectiveBooking).count() == 1

    def test_delete_venue_should_abort_when_pricing_point_for_another_venue(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue_to_delete, managingOfferer=venue_to_delete.managingOfferer)

        with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        assert exception.value.errors["cannotDeleteVenueUsedAsPricingPointException"] == [
            "Partenaire culturel non supprimable car il est utilisé comme point de valorisation d'un autre partenaire culturel"
        ]
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offerers_models.VenuePricingPointLink).count() == 2

    def test_delete_venue_should_abort_when_there_is_no_other_venue(self):
        venue_to_delete = offerers_factories.VenueFactory()

        with pytest.raises(offerers_exceptions.CannotDeleteLastVenue) as exception:
            offerers_api.delete_venue(venue_to_delete.id)

        assert exception.value.errors["CannotDeleteLastVenue"] == [
            "Partenaire culturel non supprimable car c'est le seul SIRET de l'entité juridique"
        ]
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1

    def test_delete_venue_remove_former_pricing_point_for_another_venue(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenuePricingPointLinkFactory.create_batch(
            2,  # other venues
            pricingPoint=venue_to_delete,
            timespan=[
                date_utils.get_naive_utc_now() - datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=5),
            ],
        )
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 3
        assert db.session.query(offerers_models.VenuePricingPointLink).count() == 0

    def test_delete_venue_should_abort_when_pricing_exists_on_former_pricing_point_link(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        links = offerers_factories.VenuePricingPointLinkFactory.create_batch(
            2,
            pricingPoint=venue_to_delete,
            timespan=[
                date_utils.get_naive_utc_now() - datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=5),
            ],
        )
        finance_event = finance_factories.FinanceEventFactory(
            venue=links[1].venue,
            pricingPoint=venue_to_delete,
            pricingOrderingDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=7),
        )
        finance_factories.PricingFactory(
            booking=finance_event.booking, pricingPoint=venue_to_delete, event=finance_event
        )

        with pytest.raises(offerers_exceptions.CannotDeleteVenueUsedAsPricingPointException):
            offerers_api.delete_venue(venue_to_delete.id)

    def test_delete_venue_should_abort_when_finance_event_is_linked_to_venue(self):
        venue_to_delete = offerers_factories.VenueFactory(pricing_point="self")
        finance_factories.FinanceEventFactory(
            venue=venue_to_delete,
            pricingPoint=offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer),
        )

        with pytest.raises(offerers_exceptions.CannotDeleteVenueLinkedToFinanceEventException):
            offerers_api.delete_venue(venue_to_delete.id)

    def test_delete_venue_should_remove_offers_stocks_and_activation_codes(self):
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

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(offers_models.Stock).count() == 1
        assert db.session.query(offers_models.ActivationCode).count() == 1
        assert db.session.query(offers_models.PriceCategory).count() == 1
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 1

    def test_delete_venue_should_remove_collective_offers_stocks_and_templates(self):
        venue_to_delete = offerers_factories.VenueFactory()
        educational_factories.CollectiveOfferFactory(venue=venue_to_delete)
        template1 = educational_factories.CollectiveOfferTemplateFactory(venue=venue_to_delete)
        educational_factories.EducationalRedactorWithFavoriteCollectiveOfferTemplateFactory(
            favoriteCollectiveOfferTemplates=[template1]
        )
        educational_factories.CollectiveStockFactory(collectiveOffer__venue=venue_to_delete)
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer=venue_to_delete.managingOfferer
        )
        educational_factories.CollectiveOfferRequestFactory(collectiveOfferTemplate=template1)

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(educational_models.CollectiveOffer).count() == 1
        assert db.session.query(educational_models.CollectiveOfferTemplate).count() == 0
        assert db.session.query(educational_models.CollectiveStock).count() == 1
        assert db.session.query(educational_models.CollectiveOfferRequest).count() == 0

    def test_delete_venue_should_remove_pricing_point_links(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        remaining_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue.id).all() == [(remaining_venue.id,)]
        assert db.session.query(offerers_models.VenuePricingPointLink).count() == 0

    def test_delete_venue_should_remove_mediations_of_managed_offers(self):
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offers_factories.MediationFactory(offer__venue=venue_to_delete)
        offers_factories.MediationFactory(offer__venue=venue)
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(offers_models.Mediation).count() == 1

    def test_delete_venue_should_remove_reports_of_managed_offers(self):
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offers_factories.OfferReportFactory(offer__venue=venue_to_delete)
        offers_factories.OfferReportFactory(offer__venue=venue)
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(offers_models.OfferReport).count() == 1

    def test_delete_venue_should_remove_favorites_of_managed_offers(self):
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        users_factories.FavoriteFactory(offer__venue=venue_to_delete)
        users_factories.FavoriteFactory(offer__venue=venue)
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(users_models.Favorite).count() == 1

    def test_delete_venue_should_remove_criterions(self):
        offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
        )
        offer_venue_to_delete = offers_factories.OfferFactory(
            venue=offerers_factories.VenueFactory(), criteria=[criteria_factories.CriterionFactory()]
        )
        offerers_factories.VenueFactory(managingOfferer=offer_venue_to_delete.venue.managingOfferer)  # remaining venue

        offerers_api.delete_venue(offer_venue_to_delete.venue.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(criteria_models.OfferCriterion).count() == 1
        assert db.session.query(criteria_models.Criterion).count() == 2

    def test_delete_venue_should_remove_synchronization_to_provider(self):
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        providers_factories.VenueProviderFactory(venue=venue_to_delete)
        providers_factories.VenueProviderFactory(venue=venue)
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(providers_models.VenueProvider).count() == 1
        assert db.session.query(providers_models.Provider).count() > 0

    def test_delete_venue_should_remove_synchronization_to_allocine_provider(self):
        venue = offerers_factories.VenueFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        providers_factories.AllocineVenueProviderFactory(venue=venue_to_delete)
        providers_factories.AllocineVenueProviderFactory(venue=venue)
        providers_factories.AllocinePivotFactory(venue=venue_to_delete)
        providers_factories.AllocinePivotFactory(venue=venue, theaterId="ABCDEFGHIJKLMNOPQR==", internalId="PABCDE")
        offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)  # remaining venue

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(providers_models.VenueProvider).count() == 1
        assert db.session.query(providers_models.AllocineVenueProvider).count() == 1
        assert db.session.query(providers_models.AllocinePivot).count() == 1
        assert db.session.query(providers_models.Provider).count() > 0

    def test_delete_venue_when_template_has_offer_on_other_venue(self):
        venue = offerers_factories.VenueFactory()
        venue2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        offer = educational_factories.CollectiveOfferFactory(venue=venue2, template=template)
        offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(educational_models.CollectiveOffer).count() == 1
        assert db.session.query(educational_models.CollectiveOfferTemplate).count() == 0
        assert offer.template is None

    def test_delete_venue_should_remove_links(self):
        bank_account = finance_factories.BankAccountFactory()
        venue_to_delete = offerers_factories.VenueFactory()
        offerers_factories.VenueBankAccountLinkFactory(venue=venue_to_delete, bankAccount=bank_account)
        bank_account_id = bank_account.id
        remaining_venue = offerers_factories.VenueFactory(managingOfferer=venue_to_delete.managingOfferer)

        offerers_api.delete_venue(venue_to_delete.id)

        assert db.session.query(offerers_models.Venue.id).all() == [(remaining_venue.id,)]
        assert db.session.query(offerers_models.VenueBankAccountLink).count() == 0
        assert (
            db.session.query(finance_models.BankAccount)
            .filter(finance_models.BankAccount.id == bank_account_id)
            .one_or_none()
        )

    def test_delete_venue_should_remove_playlist(self):
        venue = offerers_factories.CollectiveVenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        educational_factories.PlaylistFactory(venue=None, collective_offer_template=template)
        educational_factories.PlaylistFactory(venue=venue, collective_offer_template=None)
        remaining_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue.id).all() == [(remaining_venue.id,)]
        assert db.session.query(educational_models.CollectivePlaylist).count() == 0

    @pytest.mark.parametrize(
        "timespan",
        [
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=150),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=50),
            ],
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
                None,
            ],
            [
                date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() + datetime.timedelta(days=30),
            ],
        ],
    )
    def test_delete_venue_should_abort_when_venue_has_active_or_future_custom_reimbursement_rule(self, timespan):
        venue = offerers_factories.VenueFactory()
        finance_factories.CustomReimbursementRuleFactory(venue=venue, offer=None, timespan=timespan)

        with pytest.raises(offerers_exceptions.CannotDeleteVenueWithActiveOrFutureCustomReimbursementRule):
            offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 1

    @pytest.mark.parametrize(
        "factory",
        [
            providers_factories.CDSCinemaDetailsFactory,
            providers_factories.BoostCinemaDetailsFactory,
            providers_factories.CGRCinemaDetailsFactory,
            providers_factories.EMSCinemaDetailsFactory,
        ],
    )
    def test_delete_venue_with_pivot(self, factory):
        detail = factory()
        venue = detail.cinemaProviderPivot.venue
        remaining_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue.id).all() == [(remaining_venue.id,)]
        assert db.session.query(factory._meta.model).count() == 0

    def test_delete_venue_with_allocine_pivot(self):
        detail = providers_factories.AllocinePivotFactory()
        venue = detail.venue
        remaining_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        offerers_api.delete_venue(venue.id)

        assert db.session.query(offerers_models.Venue.id).all() == [(remaining_venue.id,)]
        assert db.session.query(providers_models.AllocinePivot).count() == 0


class EditVenueContactTest:
    def test_create_venue_contact(self, app):
        user_offerer = offerers_factories.UserOffererFactory(
            user__email="user.pro@test.com",
        )
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
        contact_data = offerers_schemas.VenueContactModel(
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

        contact_data = offerers_schemas.VenueContactModel(
            email="other.contact@venue.com", socialMedias={"instagram": "https://instagram.com/@venue"}
        )

        venue = offerers_api.upsert_venue_contact(venue, contact_data)

        assert venue.contact
        assert venue.contact.email == contact_data.email
        assert venue.contact.social_medias == contact_data.social_medias
        assert not venue.contact.phone_number


class ApiKeyTest:
    def test_get_provider_from_api_key(self):
        value = "development_prefix_a very secret key"
        offerer = offerers_factories.OffererFactory()
        provider = providers_factories.ProviderFactory(localClass=None, name="RiotRecords")
        providers_factories.OffererProviderFactory(offerer=offerer, provider=provider)
        offerers_factories.ApiKeyFactory(provider=provider, prefix="development_prefix", secret="a very secret key")

        with assert_num_queries(1):
            found_api_key = offerers_api.find_api_key(value)

        assert found_api_key.provider == provider

    def test_no_key_found(self):
        assert not offerers_api.find_api_key("")
        assert not offerers_api.find_api_key("idonotexist")
        assert not offerers_api.find_api_key("development_prefix_value")


class CreateOffererTest:
    def test_create_offerer_if_siren_is_not_already_registered(self):
        # Given
        gen_offerer_tags()
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="777084112",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name
        assert created_offerer.siren == offerer_informations.siren
        assert created_offerer.validationStatus == ValidationStatus.NEW
        assert created_offerer.isActive
        assert "Collectivité" in (tag.label for tag in created_offerer.tags)

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert created_user_offerer.dateCreated is not None

        assert not created_user_offerer.user.has_pro_role

        actions_list = db.session.query(history_models.ActionHistory).all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

    def test_create_new_offerer_attachment_if_siren_is_already_registered(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
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

        actions_list = db.session.query(history_models.ActionHistory).all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.USER_OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == offerer

    def test_keep_offerer_validation_token_if_siren_is_already_registered_but_not_validated(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )
        offerer = offerers_factories.PendingOffererFactory(siren=offerer_informations.siren)

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

    def test_create_offerer_if_siren_was_previously_rejected(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name=offerer_informations.name,
            siren=offerer_informations.siren,
        )
        first_creation_date = offerer.dateCreated
        offerers_factories.VenueFactory(managingOfferer=offerer)

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.id == offerer.id
        assert created_offerer.name == offerer_informations.name
        assert created_offerer.siren == offerer_informations.siren
        assert created_offerer.validationStatus == ValidationStatus.NEW
        assert created_offerer.isActive
        assert created_offerer.dateCreated > first_creation_date

        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert created_user_offerer.dateCreated is not None

        assert not created_user_offerer.user.has_pro_role

        actions_list = db.session.query(history_models.ActionHistory).all()
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

        assert not offerer.managedVenues

    def test_create_offerer_if_siren_was_previously_rejected_on_user_rejected(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name=offerer_informations.name,
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

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
        created_offerer = updated_user_offerer.offerer
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer
        assert actions_list[0].comment == "Nouvelle demande sur un SIREN précédemment rejeté"

    def test_create_offerer_if_siren_was_previously_rejected_on_user_deleted(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
            latitude=48,
            longitude=2,
        )
        offerer = offerers_factories.RejectedOffererFactory(
            name=offerer_informations.name,
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

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
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
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
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

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
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
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
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

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
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

    def test_create_new_offerer_twice(self):
        # Given
        user = users_factories.NonAttachedProFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )

        # When
        offerers_api.create_offerer(user, offerer_informations)
        user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = user_offerer.offerer
        assert created_offerer.validationStatus == ValidationStatus.NEW
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED
        assert user_offerer.dateCreated is not None

        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

        actions_list = user.action_history
        assert len(actions_list) == 1
        assert actions_list[0].actionType == history_models.ActionType.OFFERER_NEW
        assert actions_list[0].authorUser == user
        assert actions_list[0].user == user
        assert actions_list[0].offerer == created_offerer

    def test_create_new_offerer_on_known_offerer_by_user_deleted(self):
        # Given
        user = users_factories.UserFactory()
        offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer",
            siren="418166096",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
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

        actions_list = (
            db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.actionType).all()
        )
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
            name="Test Offerer",
            siren="777084112",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )

        # When
        created_user_offerer = offerers_api.create_offerer(user, offerer_informations)

        # Then
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == offerer_informations.name

    @pytest.mark.settings(NATIONAL_PARTNERS_EMAIL_DOMAINS="howdy.com,partner.com")
    def test_create_offerer_national_partner_autotagging(self):
        # Given
        national_partner_tag = offerers_factories.OffererTagFactory(name="partenaire-national")
        not_a_partner_user = users_factories.UserFactory(email="noël.flantier@example.com")
        partner_user = users_factories.UserFactory(email="ssap.erutluc@partner.com")
        not_a_partner_offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer Not Partner",
            siren="777084112",
            street="123 rue de Paris",
            postalCode="93100",
            city="Montreuil",
        )
        partner_offerer_informations = offerers_serialize.CreateOffererQueryModel(
            name="Test Offerer Partner",
            siren="777084121",
            street="123 rue de Paname",
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
        offerer = offerers_factories.OffererFactory()
        author = users_factories.UserFactory()

        offerers_api.update_offerer(offerer, author, name="Test")
        offerer = db.session.query(offerers_models.Offerer).one()
        assert offerer.name == "Test"

    def test_update_offerer_logs_action(self):
        offerer = offerers_factories.OffererFactory(name="Original")
        author = users_factories.UserFactory()

        offerers_api.update_offerer(offerer, author, name="Updated")

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.INFO_MODIFIED
        assert action.actionDate is not None
        assert action.authorUserId == author.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.extraData["modified_info"] == {"name": {"new_info": "Updated", "old_info": "Original"}}


class DeleteOffererTest:
    def test_delete_cascade_offerer_should_abort_when_offerer_is_linked_to_provider(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        providers_factories.OffererProviderFactory(offerer=offerer_to_delete)

        # When
        with pytest.raises(offerers_exceptions.CannotDeleteOffererLinkedToProvider) as exception:
            offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert exception.value.errors["cannotDeleteOffererLinkedToProvider"] == [
            "Entité juridique non supprimable car elle est liée à un provider"
        ]
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.OffererProvider).count() == 1

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
            "Entité juridique non supprimable car elle contient des réservations"
        ]
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(offers_models.Offer).count() == 2
        assert db.session.query(offers_models.Stock).count() == 1
        assert db.session.query(bookings_models.Booking).count() == 1

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
            "Entité juridique non supprimable car elle contient des réservations"
        ]
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 2
        assert db.session.query(educational_models.CollectiveOffer).count() == 2
        assert db.session.query(educational_models.CollectiveStock).count() == 1
        assert db.session.query(educational_models.CollectiveBooking).count() == 1

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
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Offer).count() == 2
        assert db.session.query(offers_models.Stock).count() == 2
        assert db.session.query(offers_models.ActivationCode).count() == 1
        assert db.session.query(offers_models.PriceCategory).count() == 1
        assert db.session.query(offers_models.PriceCategoryLabel).count() == 1

    def test_delete_cascade_offerer_should_remove_all_user_attachments_to_deleted_offerer(self):
        # Given
        pro = users_factories.ProFactory()
        offerer_to_delete = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer_to_delete)
        offerers_factories.UserOffererFactory(user=pro)

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.UserOfferer).count() == 1

    def test_delete_cascade_offerer_should_remove_offers_of_offerer(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer_to_delete)
        offers_factories.EventOfferFactory(venue=venue)
        offers_factories.ThingOfferFactory(venue=venue)

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offers_models.Offer).count() == 0

    def test_delete_cascade_offerer_should_remove_pricing_point_links(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        offerers_factories.VenueFactory(pricing_point=venue, managingOfferer=venue.managingOfferer)
        offerer = venue.managingOfferer

        offerers_api.delete_offerer(offerer.id)

        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(offerers_models.Venue).count() == 0
        assert db.session.query(offerers_models.VenuePricingPointLink).count() == 0

    def test_delete_cascade_offerer_should_remove_mediations_of_managed_offers(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        offers_factories.MediationFactory(offer__venue__managingOfferer=offerer_to_delete)
        offers_factories.MediationFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(offers_models.Mediation).count() == 1

    def test_delete_cascade_offerer_should_remove_favorites_of_managed_offers(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        users_factories.FavoriteFactory(offer__venue__managingOfferer=offerer_to_delete)
        users_factories.FavoriteFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(users_models.Favorite).count() == 1

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
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(offers_models.Offer).count() == 1
        assert db.session.query(criteria_models.OfferCriterion).count() == 1
        assert db.session.query(criteria_models.Criterion).count() == 2

    def test_delete_cascade_offerer_should_remove_venue_synchronization_to_provider(self):
        # Given
        offerer_to_delete = offerers_factories.OffererFactory()
        providers_factories.VenueProviderFactory(venue__managingOfferer=offerer_to_delete)
        providers_factories.VenueProviderFactory()

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(providers_models.VenueProvider).count() == 1
        assert db.session.query(providers_models.Provider).count() > 0

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
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(providers_models.VenueProvider).count() == 1
        assert db.session.query(providers_models.AllocineVenueProvider).count() == 1
        assert db.session.query(providers_models.AllocinePivot).count() == 1
        assert db.session.query(providers_models.Provider).count() > 0

    def test_delete_cascade_offerer_should_remove_related_bank_account(self):
        # Given
        bank_account = finance_factories.BankAccountFactory()
        offerer_to_delete = bank_account.offerer

        # When
        offerers_api.delete_offerer(offerer_to_delete.id)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(finance_models.BankAccount).count() == 0

    def test_delete_cascade_offerer_should_remove_collective_templates_and_playlists(self):
        # Given
        venue = offerers_factories.CollectiveVenueFactory()
        template = educational_factories.CollectiveOfferTemplateFactory(venue=venue)
        educational_factories.EducationalRedactorWithFavoriteCollectiveOfferTemplateFactory(
            favoriteCollectiveOfferTemplates=[template]
        )
        educational_factories.PlaylistFactory(venue=venue, collective_offer_template=None)
        educational_factories.PlaylistFactory(venue=None, collective_offer_template=template)

        # When
        offerers_api.delete_offerer(venue.managingOffererId)

        # Then
        assert db.session.query(offerers_models.Offerer).count() == 0
        assert db.session.query(educational_models.CollectiveOfferTemplate).count() == 0
        assert db.session.query(educational_models.CollectivePlaylist).count() == 0

    @pytest.mark.parametrize(
        "timespan",
        [
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=50),
            ],
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
                None,
            ],
            [
                date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() + datetime.timedelta(days=30),
            ],
        ],
    )
    def test_delete_cascade_offerer_should_abort_when_offerer_has_active_or_future_custom_reimbursement_rule(
        self, timespan
    ):
        offerer = offerers_factories.OffererFactory()
        finance_factories.CustomReimbursementRuleFactory(offerer=offerer, offer=None, timespan=timespan)

        with pytest.raises(offerers_exceptions.CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule):
            offerers_api.delete_offerer(offerer.id)

        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 1

    @pytest.mark.parametrize(
        "timespan",
        [
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
                date_utils.get_naive_utc_now() - datetime.timedelta(days=50),
            ],
            [
                date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
                date_utils.get_naive_utc_now() + datetime.timedelta(days=30),
            ],
            [
                date_utils.get_naive_utc_now() + datetime.timedelta(days=10),
                date_utils.get_naive_utc_now() + datetime.timedelta(days=30),
            ],
        ],
    )
    def test_delete_cascade_offerer_should_abort_when_venue_has_active_or_future_custom_reimbursement_rule(
        self, timespan
    ):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        finance_factories.CustomReimbursementRuleFactory(venue=venue, offer=None, timespan=timespan)

        with pytest.raises(offerers_exceptions.CannotDeleteOffererWithActiveOrFutureCustomReimbursementRule):
            offerers_api.delete_offerer(offerer.id)

        assert db.session.query(offerers_models.Offerer).count() == 1
        assert db.session.query(offerers_models.Venue).count() == 1
        assert db.session.query(finance_models.CustomReimbursementRule).count() == 1


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
        user_offerer = offerers_factories.NewUserOffererFactory(user=applicant)

        # When
        offerers_api.validate_offerer_attachment(user_offerer, admin)

        # Then
        assert user_offerer.validationStatus == ValidationStatus.VALIDATED

    def test_pro_role_is_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        applicant = users_factories.UserFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=applicant)

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
        user_offerer = offerers_factories.NewUserOffererFactory(user=applicant)

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
        user_offerer = offerers_factories.NewUserOffererFactory(user=invited_user)
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
        user_offerer = offerers_factories.NewUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        user_offerer_query = db.session.query(offerers_models.UserOfferer)
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.REJECTED

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_rejection_email_to_pro", return_value=True)
    def test_send_rejection_confirmation_email(self, send_offerer_attachment_rejection_email_to_pro):
        # Given
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.NewUserOffererFactory()

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        send_offerer_attachment_rejection_email_to_pro.assert_called_once_with(user_offerer)

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=user, offerer=offerer)

        # When
        offerers_api.reject_offerer_attachment(user_offerer, admin)

        # Then
        action = db.session.query(history_models.ActionHistory).one()
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
        user_offerer = offerers_factories.NewUserOffererFactory()

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        user_offerer_query = db.session.query(offerers_models.UserOfferer)
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.DELETED

    def test_pro_role_is_not_added_to_user(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=user)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        assert not user.has_pro_role
        assert user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        # Given
        admin = users_factories.AdminFactory()
        validated_user_offerer = offerers_factories.UserOffererFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=validated_user_offerer.user)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        assert validated_user_offerer.user.has_pro_role

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.NewUserOffererFactory(user=user, offerer=offerer)

        # When
        offerers_api.delete_offerer_attachment(user_offerer, admin)

        # Then
        action = db.session.query(history_models.ActionHistory).one()
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
        another_user_on_same_offerer = offerers_factories.NewUserOffererFactory(user=another_applicant)

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
        action = db.session.query(history_models.ActionHistory).one()
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
        offerer = offerers_factories.NewOffererFactory()
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
        user_offerer_query = db.session.query(offerers_models.UserOfferer)
        assert user_offerer_query.count() == 1
        assert user_offerer_query.one().validationStatus == ValidationStatus.REJECTED

    @patch("pcapi.core.mails.transactional.send_offerer_attachment_rejection_email_to_pro")
    @patch("pcapi.core.mails.transactional.send_new_offerer_rejection_email_to_pro")
    def test_send_rejection_confirmation_email(
        self, send_new_offerer_rejection_email_to_pro, send_offerer_attachment_rejection_email_to_pro
    ):
        # Given
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)  # removed in reject_offerer()

        # When
        offerers_api.reject_offerer(offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER)

        # Then
        send_new_offerer_rejection_email_to_pro.assert_called_once_with(
            offerer, offerers_models.OffererRejectionReason.OTHER
        )
        send_offerer_attachment_rejection_email_to_pro.assert_not_called()  # one email is enough

    def test_action_is_logged(self):
        # Given
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.NewUserOffererFactory(offerer=offerer)  # another applicant

        # When
        offerers_api.reject_offerer(offerer, admin, rejection_reason=offerers_models.OffererRejectionReason.OTHER)

        # Then
        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.OFFERER_REJECTED)
            .one()
        )
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None

        action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.USER_OFFERER_REJECTED, user=user)
            .one()
        )
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId == user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Compte pro rejeté suite au rejet de l'entité juridique"


class CloseOffererTest:
    def test_offerer_was_not_validated(self):
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.NewOffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 7), author_user=admin)

        assert offerer.isClosed

    def test_offerer_was_validated(self):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 7), author_user=admin)

        assert offerer.isClosed
        assert offerer.UserOfferers == [user_offerer]
        assert user_offerer.isValidated
        assert not user_offerer.user.has_pro_role
        assert user_offerer.user.has_non_attached_pro_role

    def test_pro_role_is_not_removed_from_user(self):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer
        other_user_offerer = offerers_factories.UserOffererFactory(user=user_offerer.user)

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 7), author_user=admin)

        assert offerer.isClosed
        assert user_offerer.isValidated
        assert other_user_offerer.user.has_pro_role
        assert not other_user_offerer.user.has_non_attached_pro_role

    @patch("pcapi.core.mails.transactional.send_offerer_closed_email_to_pro")
    def test_send_offerer_closed_email(self, mock_send_offerer_closed_email_to_pro):
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 7))

        mock_send_offerer_closed_email_to_pro.assert_called_once_with(offerer, False, datetime.date(2025, 3, 7))

    @patch("pcapi.core.mails.transactional.send_offerer_closed_email_to_pro")
    def test_send_offerer_closed_manually_email(self, mock_send_offerer_closed_email_to_pro):
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer)

        offerers_api.close_offerer(offerer, is_manual=True, author_user=admin)

        mock_send_offerer_closed_email_to_pro.assert_called_once_with(offerer, True, None)

    def test_action_is_logged(self):
        admin = users_factories.AdminFactory()
        user = users_factories.UserFactory()
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=user, offerer=offerer)
        offerers_factories.UserOffererFactory(offerer=offerer)  # another user

        offerers_api.close_offerer(
            offerer,
            closure_date=datetime.date(2025, 3, 7),
            author_user=admin,
            comment="Test",
            modified_info={"tags": {"new_info": "SIREN caduc"}},
        )

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.OFFERER_CLOSED
        assert action.actionDate is not None
        assert action.authorUserId == admin.id
        assert action.userId is None
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.comment == "Test"
        assert action.extraData == {
            "modified_info": {"tags": {"new_info": "SIREN caduc"}},
            "closure_date": "2025-03-07",
        }

    def test_future_closure_date(self):
        admin = users_factories.AdminFactory()
        user_offerer = offerers_factories.UserOffererFactory()
        offerer = user_offerer.offerer

        with pytest.raises(offerers_exceptions.FutureClosureDate):
            offerers_api.close_offerer(
                offerer, closure_date=datetime.date.today() + datetime.timedelta(days=1), author_user=admin
            )

        assert offerer.isValidated

    def test_close_offerer_with_thing_bookings(self):
        admin = users_factories.AdminFactory()
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        confirmed_booking = bookings_factories.BookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue=venue)
        )
        used_booking = bookings_factories.UsedBookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue=venue)
        )
        canceled_booking = bookings_factories.CancelledBookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue=venue),
            cancellationReason=bookings_models.BookingCancellationReasons.BENEFICIARY,
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(
            stock=offers_factories.ThingStockFactory(offer__venue=venue)
        )
        other_booking = bookings_factories.BookingFactory(
            stock=offers_factories.ThingStockFactory(), user=confirmed_booking.user
        )
        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 26), author_user=admin)

        assert offerer.isClosed

        # canceled:
        assert confirmed_booking.status == bookings_models.BookingStatus.CANCELLED
        assert confirmed_booking.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER_CLOSED

        # unchanged:
        assert used_booking.status == bookings_models.BookingStatus.USED
        assert canceled_booking.status == bookings_models.BookingStatus.CANCELLED
        assert canceled_booking.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        assert reimbursed_booking.status == bookings_models.BookingStatus.REIMBURSED
        assert other_booking.status == bookings_models.BookingStatus.CONFIRMED

        # no user_offerer in this test, 1 booking canceled
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[0]["To"] == confirmed_booking.user.email
        assert mails_testing.outbox[0]["params"]["OFFER_NAME"] == confirmed_booking.stock.offer.name
        assert mails_testing.outbox[0]["params"]["REASON"] == "OFFERER_CLOSED"

    def test_close_offerer_with_event_bookings(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        confirmed_booking_2_days_ago = bookings_factories.BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue=venue, beginningDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=2)
            )
        )
        confirmed_booking_in_2_days = bookings_factories.BookingFactory(
            stock=offers_factories.EventStockFactory(
                offer__venue=venue, beginningDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=2)
            )
        )

        used_booking = bookings_factories.UsedBookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue=venue)
        )
        canceled_booking = bookings_factories.CancelledBookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue=venue),
            cancellationReason=bookings_models.BookingCancellationReasons.BENEFICIARY,
        )
        reimbursed_booking = bookings_factories.ReimbursedBookingFactory(
            stock=offers_factories.EventStockFactory(offer__venue=venue)
        )
        other_booking = bookings_factories.BookingFactory(stock=offers_factories.EventStockFactory())

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 20))

        assert offerer.isClosed

        # canceled:
        assert confirmed_booking_in_2_days.status == bookings_models.BookingStatus.CANCELLED
        assert (
            confirmed_booking_in_2_days.cancellationReason == bookings_models.BookingCancellationReasons.OFFERER_CLOSED
        )

        # unchanged:
        assert confirmed_booking_2_days_ago.status == bookings_models.BookingStatus.CONFIRMED
        assert used_booking.status == bookings_models.BookingStatus.USED
        assert canceled_booking.status == bookings_models.BookingStatus.CANCELLED
        assert canceled_booking.cancellationReason == bookings_models.BookingCancellationReasons.BENEFICIARY
        assert reimbursed_booking.status == bookings_models.BookingStatus.REIMBURSED
        assert other_booking.status == bookings_models.BookingStatus.CONFIRMED

        # no user_offerer in this test, 1 booking canceled
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.BOOKING_CANCELLATION_BY_PRO_TO_BENEFICIARY.value
        )
        assert mails_testing.outbox[0]["To"] == confirmed_booking_in_2_days.user.email
        assert mails_testing.outbox[0]["params"]["OFFER_NAME"] == confirmed_booking_in_2_days.stock.offer.name
        assert mails_testing.outbox[0]["params"]["REASON"] == "OFFERER_CLOSED"

    def test_close_offerer_with_collective_bookings(self):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)

        pending_booking = educational_factories.PendingCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__startDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=1),
            collectiveStock__endDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(hours=1),
        )
        confirmed_booking_ends_2_days_ago = educational_factories.ConfirmedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__startDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
            collectiveStock__endDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=2),
        )
        confirmed_booking_started_which_ends_in_2_days = educational_factories.ConfirmedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__startDatetime=date_utils.get_naive_utc_now() - datetime.timedelta(days=1),
            collectiveStock__endDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=2),
        )
        confirmed_booking_starts_in_4_days = educational_factories.ConfirmedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__startDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=4),
            collectiveStock__endDatetime=date_utils.get_naive_utc_now() + datetime.timedelta(days=6),
        )
        used_booking = educational_factories.UsedCollectiveBookingFactory(collectiveStock__collectiveOffer__venue=venue)
        reimbursed_booking = educational_factories.ReimbursedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue
        )
        canceled_booking = educational_factories.CancelledCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=venue,
            cancellationReason=educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER,
        )
        other_booking = educational_factories.PendingCollectiveBookingFactory()

        offerers_api.close_offerer(offerer, closure_date=datetime.date(2025, 3, 20))

        assert offerer.isClosed

        # canceled:
        for booking in (
            pending_booking,
            confirmed_booking_started_which_ends_in_2_days,
            confirmed_booking_starts_in_4_days,
        ):
            assert booking.status == educational_models.CollectiveBookingStatus.CANCELLED
            assert booking.cancellationReason == educational_models.CollectiveBookingCancellationReasons.OFFERER_CLOSED

        # unchanged:
        assert confirmed_booking_ends_2_days_ago.status == educational_models.CollectiveBookingStatus.CONFIRMED
        assert used_booking.status == educational_models.CollectiveBookingStatus.USED
        assert canceled_booking.status == educational_models.CollectiveBookingStatus.CANCELLED
        assert (
            canceled_booking.cancellationReason
            == educational_models.CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER
        )
        assert reimbursed_booking.status == educational_models.CollectiveBookingStatus.REIMBURSED
        assert other_booking.status == educational_models.CollectiveBookingStatus.PENDING

        # no user_offerer in this test, no transactional email for EAC
        assert len(mails_testing.outbox) == 0


class AutoDeleteAttachmentsOnClosedOfferersTest:
    @pytest.mark.parametrize(
        "validation_status_before,validation_status_after,action_type",
        [
            (ValidationStatus.NEW, ValidationStatus.REJECTED, history_models.ActionType.USER_OFFERER_REJECTED),
            (ValidationStatus.PENDING, ValidationStatus.REJECTED, history_models.ActionType.USER_OFFERER_REJECTED),
            (ValidationStatus.VALIDATED, ValidationStatus.DELETED, history_models.ActionType.USER_OFFERER_DELETED),
            (ValidationStatus.REJECTED, ValidationStatus.REJECTED, None),
            (ValidationStatus.DELETED, ValidationStatus.DELETED, None),
        ],
    )
    def test_depending_on_user_offerer_validation(self, validation_status_before, validation_status_after, action_type):
        offerer = offerers_factories.ClosedOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer, validationStatus=validation_status_before)
        history_factories.ActionHistoryFactory(
            actionDate=datetime.datetime(2025, 1, 21),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )

        offerers_api.auto_delete_attachments_on_closed_offerers()

        assert user_offerer.validationStatus == validation_status_after
        if action_type is None:
            assert len(user_offerer.user.action_history) == 0
        else:
            assert len(user_offerer.user.action_history) == 1
            action = user_offerer.user.action_history[0]
            assert action.actionType == action_type
            assert action.user == user_offerer.user
            assert (
                action.comment
                == "Délai de 90 jours expiré après fermeture de l'entité juridique sur la plateforme le 21/01/2025"
            )

    def test_less_than_deletion_delay(self):
        offerer = offerers_factories.ClosedOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=88),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )

        with assert_num_queries(1):
            offerers_api.auto_delete_attachments_on_closed_offerers()

        assert user_offerer.isValidated
        assert len(user_offerer.user.action_history) == 0

    def test_offerer_no_longer_closed(self):
        offerer = offerers_factories.OffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=95),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=85),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
            offerer=offerer,
        )

        with assert_num_queries(1):
            offerers_api.auto_delete_attachments_on_closed_offerers()

        assert user_offerer.isValidated
        assert len(user_offerer.user.action_history) == 0

    @pytest.mark.parametrize(
        "days,expected_validation_status", [(95, ValidationStatus.DELETED), (85, ValidationStatus.VALIDATED)]
    )
    def test_offerer_closed_twice(self, days, expected_validation_status):
        offerer = offerers_factories.ClosedOffererFactory()
        user_offerer = offerers_factories.UserOffererFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=98),
            actionType=history_models.ActionType.OFFERER_VALIDATED,
            offerer=offerer,
        )
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=days),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )

        offerers_api.auto_delete_attachments_on_closed_offerers()

        assert user_offerer.validationStatus == expected_validation_status

    def test_mutiple_users_on_the_same_offerer(self):
        offerer = offerers_factories.ClosedOffererFactory()
        user_offerer_list = offerers_factories.UserOffererFactory.create_batch(3, offerer=offerer)
        pending_user_offerer = offerers_factories.NewUserOffererFactory(offerer=offerer)
        history_factories.ActionHistoryFactory(
            actionDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=91),
            actionType=history_models.ActionType.OFFERER_CLOSED,
            offerer=offerer,
        )

        offerers_api.auto_delete_attachments_on_closed_offerers()

        for user_offerer in user_offerer_list:
            assert user_offerer.isDeleted
        assert pending_user_offerer.isRejected


def test_grant_user_offerer_access():
    offerer = offerers_factories.OffererFactory.build()
    user = users_factories.UserFactory.build()

    user_offerer = offerers_api.grant_user_offerer_access(offerer, user)

    assert user_offerer.user == user
    assert user_offerer.offerer == offerer
    assert user_offerer.validationStatus == ValidationStatus.VALIDATED
    assert not user.has_pro_role


class HandleclosedOffererTest:
    @pytest.fixture(name="siren_caduc_tag")
    def siren_caduc_tag_fixture(self):
        return offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc")

    pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=False)

    @patch("pcapi.core.offerers.api.close_offerer")
    @time_machine.travel("2025-01-21 12:00:00")
    def test_tag_offerer_no_delete(
        self,
        mock_close_offerer,
        client,
        siren_caduc_tag,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001")

        offerers_api.handle_closed_offerer(offerer, closure_date=datetime.date(2025, 1, 16))

        assert offerer.tags == [siren_caduc_tag]
        mock_close_offerer.assert_not_called()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    def test_inactive_offerer_already_tagged(
        self,
        mock_close_offerer,
        client,
        siren_caduc_tag,
    ):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])

        offerers_api.handle_closed_offerer(offerer, closure_date=datetime.date(2025, 1, 16))

        assert offerer.tags == [siren_caduc_tag]
        assert db.session.query(history_models.ActionHistory).count() == 0  # tag already set, no change made
        mock_close_offerer.assert_called_once()

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    @patch("pcapi.core.offerers.api.close_offerer")
    @time_machine.travel("2025-03-10 12:00:00")
    def test_close_inactive_offerer_already_tagged(self, mock_close_offerer, client, siren_caduc_tag):
        # SIREN makes offerer inactive (because of 99), late for taxes (third digit is 9), SARL (fourth digit is 5)
        offerer = offerers_factories.OffererFactory(siren="109599001", tags=[siren_caduc_tag])

        offerers_api.handle_closed_offerer(offerer, closure_date=datetime.date(2025, 1, 16))
        assert offerer.tags == [siren_caduc_tag]
        mock_close_offerer.assert_called_once_with(
            offerer,
            closure_date=datetime.date(2025, 1, 16),
            author_user=None,
            comment="L'entité juridique est détectée comme fermée le 16/01/2025 au répertoire Sirene (INSEE)",
        )

    @pytest.mark.features(ENABLE_AUTO_CLOSE_CLOSED_OFFERERS=True)
    def test_reject_inactive_offerer_waiting_for_validation(
        self,
        client,
        siren_caduc_tag,
    ):
        offerer = offerers_factories.PendingOffererFactory(siren="100099001")
        user_offerer = offerers_factories.UserNotValidatedOffererFactory(offerer=offerer)

        offerers_api.handle_closed_offerer(offerer, closure_date=datetime.date(2025, 1, 16))

        assert offerer.isRejected
        assert offerer.tags == [siren_caduc_tag]

        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.OFFERER_REJECTED)
            .one()
        )
        assert offerer_action.actionDate is not None
        assert offerer_action.authorUserId is None
        assert offerer_action.userId == user_offerer.user.id
        assert offerer_action.offererId == offerer.id
        assert offerer_action.extraData == {
            "modified_info": {"tags": {"new_info": siren_caduc_tag.label}},
            "rejection_reason": offerers_models.OffererRejectionReason.CLOSED_BUSINESS.name,
        }

        user_offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter_by(actionType=history_models.ActionType.USER_OFFERER_REJECTED)
            .one()
        )
        assert user_offerer_action.actionDate is not None
        assert user_offerer_action.authorUserId is None
        assert user_offerer_action.userId == user_offerer.user.id
        assert user_offerer_action.offererId == offerer.id

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["To"] == user_offerer.user.email
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(TransactionalEmail.NEW_OFFERER_REJECTION.value)
        assert mails_testing.outbox[0]["params"] == {
            "OFFERER_NAME": offerer.name,
            "REJECTION_REASON": offerers_models.OffererRejectionReason.CLOSED_BUSINESS.name,
        }


class VenueBannerTest:
    IMAGES_DIR = pathlib.Path(tests.__path__[0]) / "files"

    @time_machine.travel("2020-10-15 00:00:00", tick=False)
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_save_venue_banner_when_no_default_available(self, mock_search_async_index_venue_ids, tmpdir, settings):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        settings.OBJECT_STORAGE_URL = tmpdir.dirname
        settings.LOCAL_STORAGE_DIR = pathlib.Path(tmpdir.dirname)
        offerers_api.save_venue_banner(user, venue, image_content, image_credit="none")

        updated_venue = db.session.get(Venue, venue.id)
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
            reason=IndexationReason.VENUE_BANNER_UPDATE,
        )

    @time_machine.travel("2020-10-15 00:00:00", tick=False)
    @patch("pcapi.core.search.async_index_venue_ids")
    def test_save_venue_banner_when_default_available(self, mock_search_async_index_venue_ids, tmpdir, settings):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory(venueTypeCode=offerers_models.VenueTypeCode.MOVIE)
        image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        settings.OBJECT_STORAGE_URL = tmpdir.dirname
        settings.LOCAL_STORAGE_DIR = pathlib.Path(tmpdir.dirname)
        offerers_api.save_venue_banner(user, venue, image_content, image_credit="none")

        updated_venue = db.session.get(Venue, venue.id)
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
            reason=IndexationReason.VENUE_BANNER_UPDATE,
        )

    @patch("pcapi.core.search.async_index_venue_ids")
    def test_replace_venue_banner(self, mock_search_async_index_venue_ids, tmpdir, settings):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        first_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        second_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_landscape.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        settings.OBJECT_STORAGE_URL = tmpdir.dirname
        settings.LOCAL_STORAGE_DIR = pathlib.Path(tmpdir.dirname)
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
    def test_replace_venue_legacy_banner(self, mock_search_async_index_venue_ids, tmpdir, settings):
        user = users_factories.UserFactory()
        venue = offerers_factories.VenueFactory()
        first_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_full_size.jpg").read_bytes()
        second_image_content = (VenueBannerTest.IMAGES_DIR / "mouette_landscape.jpg").read_bytes()
        directory = pathlib.Path(tmpdir.dirname) / "thumbs" / "venues"

        settings.OBJECT_STORAGE_URL = tmpdir.dirname
        settings.LOCAL_STORAGE_DIR = pathlib.Path(tmpdir.dirname)
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
        assert db.session.query(offerers_models.VenuePricingPointLink).count() == 0

        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)

        db.session.rollback()  # ensure that commit() was called before assertions

        new_link = db.session.query(offerers_models.VenuePricingPointLink).one()
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
        pre_existing_link = db.session.query(offerers_models.VenuePricingPointLink).one()
        pricing_point_2 = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)

        with pytest.raises(offerers_exceptions.CannotLinkVenueToPricingPoint):
            offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id)
        assert db.session.query(offerers_models.VenuePricingPointLink).one() == pre_existing_link

        # Now force the link.
        offerers_api.link_venue_to_pricing_point(venue, pricing_point_2.id, force_link=True)
        link = (
            db.session.query(offerers_models.VenuePricingPointLink)
            .order_by(offerers_models.VenuePricingPointLink.id.desc())
            .first()
        )
        assert link.venue == venue
        assert link.pricingPoint == pricing_point_2

    def test_fails_if_venue_has_siret(self):
        pricing_point = offerers_factories.VenueFactory()
        offerer = pricing_point.managingOfferer
        venue = offerers_factories.VenueFactory(managingOfferer=offerer, siret="1234")

        with pytest.raises(api_errors.ApiErrors) as error:
            offerers_api.link_venue_to_pricing_point(venue, pricing_point.id)
        msg = "Ce partenaire culturel a un SIRET, vous ne pouvez donc pas choisir un autre partenaire culturel pour le calcul du barème de remboursement."
        assert error.value.errors == {"pricingPointId": [msg]}


class HasVenueAtLeastOneBookableOfferTest:
    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_eligible(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offers_factories.EventStockFactory(offer__venue=venue)

        assert offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_no_offers(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_managing_offerer_not_validated(self):
        venue = offerers_factories.VenueFactory(
            isPermanent=True, managingOfferer=offerers_factories.NewOffererFactory()
        )
        offers_factories.EventStockFactory(offer__venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_offer_without_stock(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)
        offers_factories.OfferFactory(venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_expired_event(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)

        one_week_ago = date_utils.get_naive_utc_now() - datetime.timedelta(days=7)
        offers_factories.EventStockFactory(beginningDatetime=one_week_ago, offer__venue=venue)

        assert not offerers_api.has_venue_at_least_one_bookable_offer(venue)

    @pytest.mark.features(ENABLE_VENUE_STRICT_SEARCH=True)
    def test_only_one_bookable_offer(self):
        venue = offerers_factories.VenueFactory(isPermanent=True)

        # offer with bookable stock: venue is eligible
        offers_factories.EventStockFactory(offer__venue=venue)

        # without the previous offer, the venue would not be eligible
        one_week_ago = date_utils.get_naive_utc_now() - datetime.timedelta(days=7)
        offers_factories.EventStockFactory(beginningDatetime=one_week_ago, offer__venue=venue)

        assert offerers_api.has_venue_at_least_one_bookable_offer(venue)


class GetOffererTotalRevenueTest:
    def _create_data(self):
        today = datetime.datetime.now(datetime.timezone.utc)
        offerer = offerers_factories.OffererFactory()
        bookings_factories.BookingFactory(stock__offer__venue__managingOfferer=offerer, stock__price=10)
        bookings_factories.UsedBookingFactory(
            stock__offer__venue__managingOfferer=offerer,
            stock__price=11.5,
            dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(days=400),
        )
        bookings_factories.ReimbursedBookingFactory(
            stock__offer__venue__managingOfferer=offerer, stock__price=12, quantity=2
        )
        bookings_factories.CancelledBookingFactory(stock__offer__venue__managingOfferer=offerer, stock__price=120)
        educational_factories.PendingCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer, collectiveStock__price=1333
        )
        educational_factories.UsedCollectiveBookingFactory(
            dateUsed=today,
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__price=1444,
        )
        educational_factories.ReimbursedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer,
            collectiveStock__price=1555,
            dateUsed=date_utils.get_naive_utc_now() - datetime.timedelta(days=500),
        )
        educational_factories.CancelledCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=offerer, collectiveStock__price=6000
        )
        bookings_factories.UsedBookingFactory(stock__price=180, user__deposit__amount=300)  # ignored
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
        assert stats == {"DELETED": 0, "NEW": 1, "PENDING": 2, "VALIDATED": 3, "REJECTED": 4, "CLOSED": 0}

    def test_get_offerer_stats_zero(self, client):
        # when
        with assert_num_queries(1):
            stats = offerers_api.count_offerers_by_validation_status()

        # then
        assert stats == {"DELETED": 0, "NEW": 0, "PENDING": 0, "VALIDATED": 0, "REJECTED": 0, "CLOSED": 0}


class UpdateOffererTagTest:
    def test_update_offerer_tag(self):
        offerer_tag = offerers_factories.OffererTagFactory(name="serious-tag-name", label="Serious Tag")

        offerers_api.update_offerer_tag(
            offerer_tag, name="not-so-serious-tag-name", label="Taggy McTagface", description="Why so serious ?"
        )
        offerer_tag = db.session.query(offerers_models.OffererTag).one()
        assert offerer_tag.name == "not-so-serious-tag-name"
        assert offerer_tag.label == "Taggy McTagface"
        assert offerer_tag.description == "Why so serious ?"


class CreateFromOnboardingDataTest:
    def assert_common_venue_attrs(self, venue: offerers_models.Venue) -> None:
        assert venue.offererAddress.address.street == "3 RUE DE VALOIS"
        assert venue.offererAddress.address.banId == "75101_9575_00003"
        assert venue.bookingEmail == "pro@example.com"
        assert venue.offererAddress.address.city == "Paris"
        assert venue.dmsToken
        assert venue.offererAddress.address.latitude == decimal.Decimal("2.30829")
        assert venue.offererAddress.address.longitude == decimal.Decimal("48.87171")
        assert venue.name == "MINISTERE DE LA CULTURE"
        assert venue.offererAddress.address.postalCode == "75001"
        assert venue.publicName == "Nom public de mon lieu"
        assert venue.activity == offerers_models.Activity.CINEMA
        assert venue.audioDisabilityCompliant is None
        assert venue.mentalDisabilityCompliant is None
        assert venue.motorDisabilityCompliant is None
        assert venue.visualDisabilityCompliant is None

    def assert_common_action_history_extra_data(self, action: history_models.ActionHistory) -> None:
        assert action.extraData["target"] == offerers_models.Target.INDIVIDUAL.name
        assert action.extraData["activity"] == offerers_models.Activity.CINEMA.name
        assert (
            action.extraData["web_presence"]
            == "https://www.example.com, https://instagram.com/example, https://mastodon.social/@example"
        )

    def assert_venue_registration_attrs(self, venue: Venue) -> None:
        assert db.session.query(offerers_models.VenueRegistration).all() == [venue.registration]
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
            address=offerers_schemas.LocationModel(
                label="",
                banId="75101_9575_00003",
                city=offerers_schemas.VenueCity("Paris"),
                latitude=2.30829,
                longitude=48.87171,
                postalCode=offerers_schemas.VenuePostalCode("75001"),
                inseeCode="75101",
                street=offerers_schemas.VenueAddress("3 RUE DE VALOIS"),
            ),
            isOpenToPublic=True,
            siret="85331845900031",
            publicName="Nom public de mon lieu",
            createVenueWithoutSiret=create_venue_without_siret,
            target=offerers_models.Target.INDIVIDUAL,
            activity=offerers_models.Activity.CINEMA.name,
            webPresence="https://www.example.com, https://instagram.com/example, https://mastodon.social/@example",
            token="token",
        )

    @pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
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
            "https://data.geopf.fr/geocodage/search?q=3 RUE DE VALOIS&postcode=75001&autocomplete=0&limit=1",
            json=api_adresse_response,
        )
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        educational_domains = educational_factories.EducationalDomainFactory.create_batch(3)

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.culturalDomains = [domain.name for domain in educational_domains]
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        address = db.session.query(geography_models.Address).one()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.validationStatus == ValidationStatus.NEW
        # User is attached to offerer
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        # but does not have PRO role yet, because the Offerer is not validated
        assert created_user_offerer.user.has_non_attached_pro_role
        # 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 1
        created_venue = created_user_offerer.offerer.managedVenues[0]

        self.assert_common_venue_attrs(created_venue)
        assert created_venue.isOpenToPublic is True
        assert created_venue.comment is None
        assert created_venue.siret == "85331845900031"
        assert created_venue.current_pricing_point_id == created_venue.id
        assert address.street == "3 RUE DE VALOIS"
        assert address.city == "Paris"
        assert address.postalCode == "75001"
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.departmentCode == "75"
        assert address.timezone == "Europe/Paris"
        assert created_venue.offererAddress == offerer_address
        assert offerer_address.addressId == address.id

        # Action logs
        assert db.session.query(history_models.ActionHistory).count() == 2
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.OFFERER_NEW)
            .one()
        )
        assert offerer_action.offerer == created_offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        venue_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED)
            .one()
        )
        assert venue_action.venue == created_venue
        assert venue_action.authorUser == user

        self.assert_only_welcome_email_to_pro_was_sent()
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

        assert set(created_venue.collectiveDomains) == set(educational_domains)

    @pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    def test_new_siren_new_siret_legacy(self, requests_mock):
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
            "https://data.geopf.fr/geocodage/search?q=3 RUE DE VALOIS&postcode=75001&autocomplete=0&limit=1",
            json=api_adresse_response,
        )
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        address = db.session.query(geography_models.Address).one()
        offerer_address = db.session.query(offerers_models.OffererAddress).one()

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        assert created_offerer.validationStatus == ValidationStatus.NEW
        # User is attached to offerer
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.VALIDATED
        # but does not have PRO role yet, because the Offerer is not validated
        assert created_user_offerer.user.has_non_attached_pro_role
        # 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 1
        created_venue = created_user_offerer.offerer.managedVenues[0]

        self.assert_common_venue_attrs(created_venue)
        assert created_venue.isOpenToPublic is True
        assert created_venue.comment is None
        assert created_venue.siret == "85331845900031"
        assert created_venue.current_pricing_point_id == created_venue.id
        assert address.street == "3 RUE DE VALOIS"
        assert address.city == "Paris"
        assert address.postalCode == "75001"
        assert address.inseeCode.startswith(address.departmentCode)
        assert address.departmentCode == "75"
        assert address.timezone == "Europe/Paris"
        assert created_venue.offererAddress == offerer_address
        assert offerer_address.addressId == address.id

        # Action logs
        assert db.session.query(history_models.ActionHistory).count() == 2
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.OFFERER_NEW)
            .one()
        )
        assert offerer_action.offerer == created_offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        venue_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED)
            .one()
        )
        assert venue_action.venue == created_venue
        assert venue_action.authorUser == user

        self.assert_only_welcome_email_to_pro_was_sent()
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

    @pytest.mark.settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    @pytest.mark.parametrize("isOpenToPublic", [True, False])
    def test_new_offerer_and_isOpenToPublic(self, isOpenToPublic, requests_mock):
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
            "https://data.geopf.fr/geocodage/search?q=3 RUE DE VALOIS&postcode=75001&autocomplete=0&limit=1",
            json=api_adresse_response,
        )
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.isOpenToPublic = isOpenToPublic
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_venue = created_user_offerer.offerer.managedVenues[0]
        assert created_venue.isOpenToPublic is isOpenToPublic

    def test_existing_siren_new_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        assert created_user_offerer.user.has_non_attached_pro_role
        # 1 venue with siret has been created
        assert len(offerer.managedVenues) == 1
        created_venue = offerer.managedVenues[0]
        self.assert_common_venue_attrs(created_venue)
        assert created_venue.comment is None
        assert created_venue.siret == "85331845900031"
        assert created_venue.current_pricing_point_id == created_venue.id
        # Action logs
        assert db.session.query(history_models.ActionHistory).count() == 2
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW)
            .one()
        )
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        venue_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED)
            .one()
        )
        assert venue_action.venue == created_venue
        assert venue_action.authorUser == user

        assert len(mails_testing.outbox) == 0
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

    def test_existing_siren_new_venue_without_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=True)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.user.has_non_attached_pro_role
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        # 1 venue without siret has been created
        assert len(offerer.managedVenues) == 1
        created_venue = offerer.managedVenues[0]
        self.assert_common_venue_attrs(created_venue)
        assert created_venue.comment == "Lieu sans SIRET car dépend du SIRET d'un autre lieu"
        assert created_venue.siret is None
        # No pricing point yet
        assert not created_venue.current_pricing_point_id
        # Action logs
        assert db.session.query(history_models.ActionHistory).count() == 2
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW)
            .one()
        )
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.VENUE_CREATED)
            .one()
        )
        assert offerer_action.venue == created_venue
        assert offerer_action.authorUser == user

        assert len(mails_testing.outbox) == 0
        # Venue Registration
        self.assert_venue_registration_attrs(created_venue)

    @pytest.mark.features(WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY=True)
    def test_existing_siren_existing_siret_is_not_a_collectivity(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        offerers_factories.VenueFactory(managingOfferer=offerer, siret="85331845900031")
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=True)

        with pytest.raises(offerers_exceptions.NotACollectivity):
            offerers_api.create_from_onboarding_data(user, onboarding_data)

    @pytest.mark.features(WIP_RESTRICT_VENUE_CREATION_TO_COLLECTIVITY=True)
    def test_existing_siren_existing_siret_is_a_collectivity(self):
        offerer = offerers_factories.OffererFactory(siren="777084112")
        offerers_factories.VenueFactory(managingOfferer=offerer, siret="77708411200031")
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=True)
        onboarding_data.siret = "77708411200031"
        offerers_api.create_from_onboarding_data(user, onboarding_data)

    def test_existing_siren_existing_siret(self):
        offerer = offerers_factories.OffererFactory(siren="853318459")
        _venue_with_siret = offerers_factories.VenueFactory(managingOfferer=offerer, siret="85331845900031")
        user = users_factories.UserFactory()
        user.add_non_attached_pro_role()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has not been created
        assert db.session.query(offerers_models.Offerer).count() == 1
        assert created_user_offerer.offerer == offerer
        # User is not attached to offerer yet
        assert created_user_offerer.userId == user.id
        assert created_user_offerer.user.has_non_attached_pro_role
        assert created_user_offerer.validationStatus == ValidationStatus.NEW
        # Venue has not been created
        assert db.session.query(offerers_models.Venue).count() == 1
        # Action logs
        assert db.session.query(history_models.ActionHistory).count() == 1
        offerer_action = (
            db.session.query(history_models.ActionHistory)
            .filter(history_models.ActionHistory.actionType == history_models.ActionType.USER_OFFERER_NEW)
            .one()
        )
        assert offerer_action.offerer == offerer
        assert offerer_action.authorUser == user
        assert offerer_action.user == user
        self.assert_common_action_history_extra_data(offerer_action)
        assert len(mails_testing.outbox) == 0
        # Venue Registration
        assert db.session.query(offerers_models.VenueRegistration).count() == 0

    def test_previously_rejected_siren_same_user(self):
        offerer = offerers_factories.RejectedOffererFactory(siren="853318459")
        rejected_venue = offerers_factories.VenueFactory(
            managingOfferer=offerer, siret="85331845900031", pricing_point="self"
        )
        rejected_venue_id = rejected_venue.id
        rejected_venue_id_without_siret = offerers_factories.VenueWithoutSiretFactory(
            managingOfferer=offerer, pricing_point=rejected_venue
        ).id
        user = users_factories.NonAttachedProFactory()
        rejected_user_offerer = offerers_factories.RejectedUserOffererFactory(user=user, offerer=offerer)

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        assert db.session.query(offerers_models.Offerer).one() == offerer
        assert offerer.isNew

        assert created_user_offerer == rejected_user_offerer
        assert created_user_offerer.offerer == offerer
        assert created_user_offerer.user == user
        assert created_user_offerer.isValidated
        assert user.has_non_attached_pro_role

        assert len(offerer.managedVenues) == 1
        venue = offerer.managedVenues[0]
        assert venue.id not in (rejected_venue_id, rejected_venue_id_without_siret)
        assert venue.publicName == onboarding_data.publicName

        actions = db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.id).all()
        assert len(actions) == 3

        assert actions[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert actions[0].offerer == offerer
        assert actions[0].authorUser == user
        assert set(actions[0].extraData["modified_info"].keys()) == {"name"}

        assert actions[1].actionType == history_models.ActionType.OFFERER_NEW
        assert actions[1].offerer == offerer
        assert actions[1].user == user
        assert actions[1].authorUser == user
        self.assert_common_action_history_extra_data(actions[1])

        assert actions[2].actionType == history_models.ActionType.VENUE_CREATED
        assert actions[2].venue == venue
        assert actions[2].authorUser == user

    def test_previously_rejected_siren_other_user(self):
        offerer = offerers_factories.RejectedOffererFactory(siren="853318459")
        rejected_venue_id = offerers_factories.VenueFactory(managingOfferer=offerer, siret="85331845900031").id
        rejected_user = users_factories.NonAttachedProFactory()
        rejected_user_offerer = offerers_factories.RejectedUserOffererFactory(user=rejected_user, offerer=offerer)
        new_user = users_factories.NonAttachedProFactory()

        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        created_user_offerer = offerers_api.create_from_onboarding_data(new_user, onboarding_data)

        assert db.session.query(offerers_models.Offerer).one() == offerer
        assert offerer.isNew

        assert created_user_offerer != rejected_user_offerer
        assert created_user_offerer.offerer == offerer
        assert created_user_offerer.user == new_user
        assert created_user_offerer.isValidated
        assert new_user.has_non_attached_pro_role
        assert rejected_user_offerer.isRejected

        assert len(offerer.managedVenues) == 1
        venue = offerer.managedVenues[0]
        assert venue.id != rejected_venue_id
        assert venue.publicName == onboarding_data.publicName

        actions = db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.id).all()
        assert len(actions) == 3

        assert actions[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert actions[0].offerer == offerer
        assert actions[0].authorUser == new_user
        assert set(actions[0].extraData["modified_info"].keys()) == {"name"}

        assert actions[1].actionType == history_models.ActionType.OFFERER_NEW
        assert actions[1].offerer == offerer
        assert actions[1].user == new_user
        assert actions[1].authorUser == new_user
        self.assert_common_action_history_extra_data(actions[1])

        assert actions[2].actionType == history_models.ActionType.VENUE_CREATED
        assert actions[2].venue == venue
        assert actions[2].authorUser == new_user

    def test_missing_address(self):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()
        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.address.street = ""

        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        # 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 1
        created_venue = created_user_offerer.offerer.managedVenues[0]
        address = created_venue.offererAddress.address
        assert address.street == "n/d"
        assert address.city == "Paris"
        assert address.latitude == decimal.Decimal("2.30829")
        assert address.longitude == decimal.Decimal("48.87171")
        assert address.postalCode == "75001"

    def test_missing_ban_id(self):
        user = users_factories.UserFactory(email="pro@example.com")
        user.add_non_attached_pro_role()
        onboarding_data = self.get_onboarding_data(create_venue_without_siret=False)
        onboarding_data.address.banId = None

        created_user_offerer = offerers_api.create_from_onboarding_data(user, onboarding_data)

        # Offerer has been created
        created_offerer = created_user_offerer.offerer
        assert created_offerer.name == "MINISTERE DE LA CULTURE"
        assert created_offerer.siren == "853318459"
        # 1 Venue with siret have been created
        assert len(created_user_offerer.offerer.managedVenues) == 1
        created_venue = created_user_offerer.offerer.managedVenues[0]
        address = created_venue.offererAddress.address
        assert address.street == "3 RUE DE VALOIS"
        assert address.banId is None
        assert address.city == "Paris"
        assert address.latitude == decimal.Decimal("2.30829")
        assert address.longitude == decimal.Decimal("48.87171")
        assert address.postalCode == "75001"

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

        offerer_invitation = db.session.query(offerers_models.OffererInvitation).one()
        assert offerer_invitation.email == "new.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.PENDING
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value.id
        )

        assert db.session.query(history_models.ActionHistory).count() == 0

    def test_offerer_invitation_created_when_user_exists_and_email_not_validated(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        users_factories.UserFactory(email="new.user@example.com", isEmailValidated=False)

        offerers_api.invite_member(offerer=offerer, email="new.user@example.com", current_user=pro_user)

        offerer_invitation = db.session.query(offerers_models.OffererInvitation).one()
        assert offerer_invitation.email == "new.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.PENDING
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_NOT_VALIDATED_USER_EMAIL.value.id
        )

        assert db.session.query(history_models.ActionHistory).count() == 0

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
        offerer_invitations = db.session.query(offerers_models.OffererInvitation).all()
        assert len(offerer_invitations) == 1
        assert len(mails_testing.outbox) == 0

        assert db.session.query(history_models.ActionHistory).count() == 0

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
        offerer_invitations = db.session.query(offerers_models.OffererInvitation).all()
        assert len(offerer_invitations) == 0
        assert len(mails_testing.outbox) == 0

        assert db.session.query(history_models.ActionHistory).count() == 0

    def test_user_offerer_created_when_user_exists_and_attached_to_another_offerer(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        attached_to_other_offerer_user = users_factories.ProFactory(email="attached.user@example.com")
        offerers_factories.UserOffererFactory(user=attached_to_other_offerer_user)

        offerers_api.invite_member(offerer=offerer, email="attached.user@example.com", current_user=pro_user)

        offerer_invitation = db.session.query(offerers_models.OffererInvitation).one()
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_EXISTING_VALIDATED_USER_EMAIL.value.id
        )
        user_offerer = (
            db.session.query(offerers_models.UserOfferer)
            .filter_by(userId=attached_to_other_offerer_user.id, offererId=offerer.id)
            .one()
        )
        assert user_offerer.validationStatus == ValidationStatus.NEW
        assert offerer_invitation.email == "attached.user@example.com"
        assert offerer_invitation.userId == pro_user.id
        assert offerer_invitation.offererId == offerer.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.ACCEPTED

        actions_list = db.session.query(history_models.ActionHistory).all()
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


class InviteMembersAgainTest:
    def test_offerer_invitation_send_when_invite_again(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(user=pro_user, offerer=offerer, email="new.user@example.com")

        offerers_api.invite_member_again(offerer=offerer, email="new.user@example.com")

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0]["template"]["id_not_prod"]
            == TransactionalEmail.OFFERER_ATTACHMENT_INVITATION_NEW_USER.value.id
        )

    def test_raise_error_when_invitation_does_not_already_exist(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)

        with pytest.raises(offerers_exceptions.InviteAgainImpossibleException) as exception:
            offerers_api.invite_member_again(offerer=offerer, email="new.user@example.com")

        assert exception.value.errors["InviteAgainImpossibleException"] == [
            "Impossible de renvoyer une invitation pour ce collaborateur"
        ]
        offerer_invitations = db.session.query(offerers_models.OffererInvitation).all()
        assert len(offerer_invitations) == 0
        assert len(mails_testing.outbox) == 0


class AcceptOffererInvitationTest:
    def test_accept_offerer_invitation_when_invitation_exist(self):
        pro_user = users_factories.ProFactory(email="pro.user@example.com")
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(user=pro_user, offerer=offerer)
        offerers_factories.OffererInvitationFactory(offerer=offerer, user=pro_user, email="new.user@example.com")
        user = users_factories.UserFactory(email="new.user@example.com")

        offerers_api.accept_offerer_invitation_if_exists(user)

        new_user_offerer = (
            db.session.query(offerers_models.UserOfferer).filter_by(validationStatus=ValidationStatus.NEW).one()
        )
        offerer_invitation = db.session.query(offerers_models.OffererInvitation).one()

        assert new_user_offerer.offererId == offerer.id
        assert new_user_offerer.userId == user.id
        assert offerer_invitation.status == offerers_models.InvitationStatus.ACCEPTED

        actions_list = db.session.query(history_models.ActionHistory).all()
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

        user_offerers = db.session.query(offerers_models.UserOfferer).all()

        assert len(user_offerers) == 2
        assert db.session.query(history_models.ActionHistory).count() == 0


class DeleteExpiredOffererInvitationsTest:
    def test_delete_expired_offerer_invitations(self):
        not_expired_pending_invitation_id = offerers_factories.OffererInvitationFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=29, hours=23)
        ).id
        _expired_pending_invitation_id = offerers_factories.OffererInvitationFactory(
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=31)
        ).id
        accepted_invitation_id = offerers_factories.OffererInvitationFactory(
            status=offerers_models.InvitationStatus.ACCEPTED,
            dateCreated=date_utils.get_naive_utc_now() - datetime.timedelta(days=100),
        ).id

        offerers_api.delete_expired_offerer_invitations()

        remaining_invitation_ids = {id_ for (id_,) in db.session.query(offerers_models.OffererInvitation.id).all()}
        assert remaining_invitation_ids == {not_expired_pending_invitation_id, accepted_invitation_id}


class AccessibilityProviderTest:
    def test_set_accessibility_provider_id(self):
        venue = offerers_factories.VenueFactory(name="Une librairie de test", accessibilityProvider=None)
        offerers_api.set_accessibility_provider_id(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == "mon-lieu-chez-acceslibre"

    def test_set_accessibility_last_update_at_provider_id(self):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
        offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerers_api.set_accessibility_infos_from_provider_id(venue)
        assert venue.accessibilityProvider.lastUpdateAtProvider == datetime.datetime(2024, 3, 1, 0, 0)

    def test_set_accessibility_infos_from_provider_id(self):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
        offerers_factories.AccessibilityProviderFactory(venue=venue)
        offerers_api.set_accessibility_infos_from_provider_id(venue)
        assert venue.accessibilityProvider.externalAccessibilityData["access_modality"] == [
            acceslibre_connector.ExpectedFieldsEnum.EXTERIOR_ONE_LEVEL,
            acceslibre_connector.ExpectedFieldsEnum.ENTRANCE_ONE_LEVEL,
        ]

    @patch("pcapi.connectors.acceslibre.get_accessibility_infos")
    def test_do_not_set_accessibility_infos_from_provider_id_when_data_is_none(self, mock_get_accessibility_infos):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            offererAddress__address__postalCode="75001",
            offererAddress__address__city="Paris",
        )
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mock-slug",
            externalAccessibilityUrl="https://example.com/mock-slug",
            lastUpdateAtProvider=datetime.datetime(2024, 3, 2, 1, 0),
        )

        mock_get_accessibility_infos.side_effect = [(datetime.datetime(2025, 4, 3, 2, 1), None)]

        offerers_api.set_accessibility_infos_from_provider_id(venue)

        assert venue.accessibilityProvider.lastUpdateAtProvider == datetime.datetime(2024, 3, 2, 1, 0)
        assert venue.accessibilityProvider.externalAccessibilityId == "mock-slug"
        assert venue.accessibilityProvider.externalAccessibilityUrl == "https://example.com/mock-slug"

    @patch("pcapi.connectors.acceslibre.get_accessibility_infos")
    def test_do_not_set_accessibility_infos_from_provider_id_when_last_update_is_none(
        self, mock_get_accessibility_infos
    ):
        venue = offerers_factories.VenueFactory(
            name="Une librairie de test",
            offererAddress__address__postalCode="75001",
            offererAddress__address__city="Paris",
        )
        offerers_factories.AccessibilityProviderFactory(
            venue=venue,
            externalAccessibilityId="mock-slug",
            externalAccessibilityUrl="https://example.com/mock-slug",
            lastUpdateAtProvider=datetime.datetime(2024, 3, 2, 1, 0),
        )

        mock_get_accessibility_infos.side_effect = [
            (None, acceslibre_connector.AcceslibreInfos(slug="another-slug", url="https://example.com/another-slug"))
        ]

        offerers_api.set_accessibility_infos_from_provider_id(venue)

        assert venue.accessibilityProvider.lastUpdateAtProvider == datetime.datetime(2024, 3, 2, 1, 0)
        assert venue.accessibilityProvider.externalAccessibilityId == "mock-slug"
        assert venue.accessibilityProvider.externalAccessibilityUrl == "https://example.com/mock-slug"

    def test_synchronize_accessibility_provider_no_data(self):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
        accessibility_provider = offerers_factories.AccessibilityProviderFactory(
            venue=venue, externalAccessibilityData=None
        )
        offerers_api.synchronize_accessibility_provider(venue)
        assert accessibility_provider.externalAccessibilityData is not None

    def test_synchronize_accessibility_provider_with_new_update(self):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
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
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
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
        offerers_factories.VenueFactory.create_batch(3, isOpenToPublic=True)
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        count = offerers_api.count_open_to_public_venues_with_accessibility_provider()
        assert count == 1

    def test_get_open_to_public_venues_with_accessibility_provider(self):
        offerers_factories.VenueFactory.create_batch(3, isOpenToPublic=True)
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        venues_list = offerers_api.get_open_to_public_venues_with_accessibility_provider(batch_size=10, batch_num=0)
        assert len(venues_list) == 1
        assert venues_list[0] == venue

    def test_get_open_to_public_venues_without_accessibility_provider(self):
        offerers_factories.VenueFactory.create_batch(3, isOpenToPublic=True)
        venue = offerers_factories.VenueFactory(isOpenToPublic=True)
        offerers_factories.AccessibilityProviderFactory(venue=venue)

        venues_list = offerers_api.get_open_to_public_venues_without_accessibility_provider()
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

        venues_list = [offerers_factories.VenueFactory(isOpenToPublic=True)]
        venue = offerers_factories.VenueFactory(
            isOpenToPublic=True,
            name="Un lieu",
            offererAddress__address__postalCode="75001",
            offererAddress__address__city="Paris",
            offererAddress__address__street="3 Rue de Valois",
        )
        venues_list.append(venue)

        offerers_api.match_venue_with_new_entries(venues_list, results_by_activity)
        assert venue.external_accessibility_url == "https://une-fausse-url.com"
        assert venue.external_accessibility_id == "mon-lieu-chez-acceslibre"

    def test_acceslibre_matching(self):
        venues_list = [offerers_factories.VenueFactory(isOpenToPublic=True)]
        venue = offerers_factories.VenueFactory(
            isOpenToPublic=True,
            name="Un lieu",
            offererAddress__address__postalCode="75001",
            offererAddress__address__city="Paris",
            offererAddress__address__street="3 Rue de Valois",
        )
        venues_list.append(venue)

        # match result is given by find_new_entries_by_activity in TestingBackend class in acceslibre connector
        offerers_api.acceslibre_matching(batch_size=1000, dry_run=False, start_from_batch=1)

        assert (
            venue.external_accessibility_url == "https://acceslibre.beta.gouv.fr/app/activite/mon-lieu-chez-acceslibre/"
        )
        assert venue.external_accessibility_id == "mon-lieu-chez-acceslibre"


class MatchAcceslibreTest:
    @patch("pcapi.connectors.acceslibre.get_id_at_accessibility_provider")
    def test_match_acceslibre(self, mock_get_id_at_accessibility_provider):
        venue = offerers_factories.VenueFactory(name="Une librairie de test")
        slug = "mon-slug"
        mock_get_id_at_accessibility_provider.side_effect = [
            acceslibre_connector.AcceslibreInfos(slug=slug, url=f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/")
        ]
        offerers_api.match_acceslibre(venue)
        assert venue.accessibilityProvider.externalAccessibilityId == slug
        assert (
            venue.accessibilityProvider.externalAccessibilityUrl == f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/"
        )
        assert venue.action_history[0].extraData == {
            "modified_info": {
                "accessibilityProvider.externalAccessibilityId": {
                    "new_info": slug,
                    "old_info": None,
                },
                "accessibilityProvider.externalAccessibilityUrl": {
                    "new_info": f"https://acceslibre.beta.gouv.fr/app/erps/{slug}/",
                    "old_info": None,
                },
            }
        }


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


class OffererAddressTest:
    # TODO (prouzet, 2025-11-13) CLEAN_OA After transition, no need for this first parametrize, use OfferLocationFactory
    @pytest.mark.parametrize(
        "factory", [offerers_factories.OffererAddressFactory, offerers_factories.OfferLocationFactory]
    )
    @pytest.mark.parametrize("same_label,same_address", [[True, False], [False, True], [True, True], [False, False]])
    def test_get_or_create_offerer_address(self, same_label, same_address, factory):
        offerer = offerers_factories.OffererFactory()
        oa_1 = factory(offerer=offerer)
        other_address = geography_factories.AddressFactory(
            street="1 rue de la paix",
        )
        vl_1 = offerers_factories.VenueLocationFactory(offerer=offerer, address=oa_1.address, label=oa_1.label)
        vl_2 = offerers_factories.VenueLocationFactory(
            offerer=offerer, address=other_address, label="somethingdifferent"
        )

        oa_return = offerers_api.get_or_create_offer_location(
            offerer_id=offerer.id,
            address_id=oa_1.address.id if same_address else other_address.id,
            label=oa_1.label if same_label else "somethingdifferent",
        )
        if same_label and same_address:
            assert oa_return == oa_1
        else:
            assert oa_return.offerer == offerer
            assert oa_return != oa_1
        assert oa_return not in (vl_1, vl_2)

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
        assert len(db.session.query(geography_models.Address).all()) == 1
        if existant_address:
            assert address == old_address
        else:
            assert address.street == "1 rue de la paix"
            assert address.city == "Paris"
            assert address.postalCode == "75103"
            assert address.latitude == decimal.Decimal("40.85660")
            assert address.longitude == decimal.Decimal("1.35220")

    def test_create_offerer_address(self):
        offerer = offerers_factories.OffererFactory()
        address = geography_factories.AddressFactory()
        oa = offerers_api.create_offerer_address(offerer_id=offerer.id, address_id=address.id, label="label")
        assert oa.offerer == offerer
        assert oa.id
        assert oa.label == "label"

    def test_create_multiple_identical_offerer_address_with_label_null(self):
        offerer = offerers_factories.OffererFactory()
        address = geography_factories.AddressFactory()
        oa = offerers_api.create_offerer_address(offerer_id=offerer.id, address_id=address.id, label=None)
        oa_ = offerers_api.create_offerer_address(offerer_id=offerer.id, address_id=address.id, label=None)

        assert oa.offerer == offerer
        assert oa_.offerer == offerer
        assert oa.id
        assert oa_.id
        assert oa.label == None
        assert oa.address == oa_.address
        assert oa.label == oa_.label
        assert oa_ != oa

    def test_should_not_create_multiple_oa_with_same_label(self):
        offerer = offerers_factories.OffererFactory()
        address = geography_factories.AddressFactory()
        offerers_api.create_offerer_address(offerer_id=offerer.id, address_id=address.id, label="label")
        with pytest.raises(offerers_exceptions.OffererAddressCreationError):
            offerers_api.create_offerer_address(offerer_id=offerer.id, address_id=address.id, label="label")


class SendReminderEmailToIndividualOfferersTest:
    @patch("pcapi.core.mails.transactional.send_offerer_individual_subscription_reminder")
    def test_send_reminder_email_to_individual_offerers(self, mocked_transactional_mail):
        offerers_factories.IndividualOffererSubscriptionFactory(
            offerer__validationStatus=ValidationStatus.PENDING, isEmailSent=False
        )
        offerers_factories.IndividualOffererSubscriptionFactory(
            offerer__validationStatus=ValidationStatus.PENDING,
            dateReminderEmailSent=datetime.date.today() - datetime.timedelta(days=1),
        )
        offerers_factories.IndividualOffererSubscriptionFactory(
            offerer__validationStatus=ValidationStatus.PENDING,
            isEmailSent=True,
            dateEmailSent=datetime.date.today() - datetime.timedelta(days=15),
            isCriminalRecordReceived=False,
        )
        offerers_factories.IndividualOffererSubscriptionFactory(offerer__validationStatus=ValidationStatus.VALIDATED)
        offerers_factories.IndividualOffererSubscriptionFactory(
            offerer__validationStatus=ValidationStatus.PENDING,
            isCriminalRecordReceived=True,
            isCertificateReceived=True,
            isExperienceReceived=True,
        )
        # This one should receive an email
        offerer = offerers_factories.IndividualOffererSubscriptionFactory(
            offerer__validationStatus=ValidationStatus.PENDING,
            isEmailSent=True,
            dateEmailSent=datetime.date.today() - datetime.timedelta(days=31),
            isCriminalRecordReceived=False,
        ).offerer
        offerers_factories.UserOffererFactory(offerer=offerer)

        # 1 query to get all data
        # 1 query to update dateReminderEmailSent
        with assert_num_queries(2):
            offerers_api.send_reminder_email_to_individual_offerers()

        assert offerer.individualSubscription.isReminderEmailSent is True
        assert offerer.individualSubscription.dateReminderEmailSent == datetime.date.today()
        mocked_transactional_mail.assert_called_once_with(offerer.UserOfferers[0].user.email)


class CleanUnusedOffererAddressTest:
    def test_clean_unused_offerer_address(self, caplog):
        offerers_factories.OffererAddressFactory()
        venue = offerers_factories.VenueFactory()
        oa1 = venue.offererAddress
        oa2, oa3, oa4, _ = offerers_factories.OfferLocationFactory.create_batch(
            4, offerer=venue.managingOfferer, venue=venue
        )
        offers_factories.OfferFactory(venue=venue, offererAddress=oa2)
        educational_factories.CollectiveOfferFactory(
            venue=venue, locationType=educational_models.CollectiveLocationType.ADDRESS, offererAddress=oa3
        )
        educational_factories.CollectiveOfferTemplateFactory(
            venue=venue, locationType=educational_models.CollectiveLocationType.ADDRESS, offererAddress=oa4
        )

        with caplog.at_level(logging.INFO):
            offerers_api.clean_unused_offerer_address()

        remaining_ids = db.session.query(sa.func.array_agg(offerers_models.OffererAddress.id)).scalar()
        assert set(remaining_ids) == {oa1.id, oa2.id, oa3.id, oa4.id}

        assert caplog.records[0].message == "2 unused rows to delete in offerer_address"

    def test_nothing_to_delete(self, caplog):
        oa = offerers_factories.VenueFactory().offererAddress

        with caplog.at_level(logging.INFO):
            offerers_api.clean_unused_offerer_address()

        remaining_ids = db.session.query(sa.func.array_agg(offerers_models.OffererAddress.id)).scalar()
        assert remaining_ids == [oa.id]

        assert caplog.records[0].message == "0 unused rows to delete in offerer_address"


class GetStatsByVenueTest:
    def test_get_offers_stats_by_venue(self):
        user_offerer = offerers_factories.UserOffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)

        # 1 bookable public offers
        offer = offers_factories.OfferFactory(venue=venue, validation=OfferValidationStatus.APPROVED)
        offers_factories.StockFactory.create_batch(3, offer=offer)

        # 1 published collective offers + 1 published collective offer template = 2 published collective offers
        educational_factories.create_collective_offer_by_status(
            educational_models.CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue
        )
        educational_factories.create_collective_offer_template_by_status(
            educational_models.CollectiveOfferDisplayedStatus.PUBLISHED, venue=venue
        )

        # 1 pending public offers
        offers_factories.OfferFactory.create_batch(3, venue=venue, validation=OfferValidationStatus.PENDING)

        # 2 pending collective offers + 2 pending collective offer template = 4 pending collective offers
        # 1 of each rejected to ensure they are not counted
        educational_factories.create_collective_offer_by_status(
            educational_models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )
        educational_factories.create_collective_offer_by_status(
            educational_models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )
        educational_factories.create_collective_offer_by_status(
            educational_models.CollectiveOfferDisplayedStatus.REJECTED, venue=venue
        )
        educational_factories.create_collective_offer_template_by_status(
            educational_models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )
        educational_factories.create_collective_offer_template_by_status(
            educational_models.CollectiveOfferDisplayedStatus.UNDER_REVIEW, venue=venue
        )
        educational_factories.create_collective_offer_template_by_status(
            educational_models.CollectiveOfferDisplayedStatus.REJECTED, venue=venue
        )

        stats = offerers_api.get_offers_stats_by_venue(venue.id)

        assert stats.pending_educational_offers == 4
        assert stats.published_educational_offers == 2
        assert stats.pending_public_offers == 3
        assert stats.published_public_offers == 1

    def test_get_offers_stats_by_venue_no_offers(self):
        venue = offerers_factories.VenueFactory()

        stats = offerers_api.get_offers_stats_by_venue(venue.id)

        assert stats.pending_educational_offers == 0
        assert stats.published_educational_offers == 0
        assert stats.pending_public_offers == 0
        assert stats.published_public_offers == 0

    def test_get_offers_stats_with_no_public_offers(self):
        venue = offerers_factories.VenueFactory()
        educational_factories.PublishedCollectiveOfferFactory.create_batch(2, venue=venue)
        educational_factories.UnderReviewCollectiveOfferFactory.create_batch(2, venue=venue)

        stats = offerers_api.get_offers_stats_by_venue(venue.id)

        assert stats.pending_educational_offers == 2
        assert stats.published_educational_offers == 2
        assert stats.pending_public_offers == 0
        assert stats.published_public_offers == 0

    def test_get_offers_stats_with_no_collective_offers(self):
        venue = offerers_factories.VenueFactory()
        offers_factories.StockFactory.create_batch(
            2, offer__venue=venue, offer__validation=OfferValidationStatus.APPROVED
        )
        offers_factories.OfferFactory.create_batch(3, venue=venue, validation=OfferValidationStatus.PENDING)

        stats = offerers_api.get_offers_stats_by_venue(venue.id)

        assert stats.pending_educational_offers == 0
        assert stats.published_educational_offers == 0
        assert stats.pending_public_offers == 3
        assert stats.published_public_offers == 2
