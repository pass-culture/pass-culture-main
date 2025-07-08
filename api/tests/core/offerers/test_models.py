import datetime

import pytest
import sqlalchemy.orm as sa_orm
from sqlalchemy.exc import IntegrityError

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.schemas as offerers_schemas
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories
from pcapi.core.offerers import models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


class VenueModelConstraintsTest:
    def test_virtual_venue_cannot_have_siret(self):
        venue = factories.VirtualVenueFactory()
        with pytest.raises(IntegrityError) as err:
            venue.siret = "siret"
            db.session.add(venue)
            db.session.flush()
        assert "check_has_siret_xor_comment_xor_isVirtual" in str(err.value)

    def test_non_virtual_without_siret_must_have_comment(self):
        venue = factories.VenueWithoutSiretFactory()
        with pytest.raises(IntegrityError) as err:
            venue.comment = None
            db.session.add(venue)
            db.session.flush()
        assert "check_has_siret_xor_comment_xor_isVirtual" in str(err.value)

    def test_at_most_one_virtual_venue_per_offerer(self):
        virtual_venue1 = factories.VirtualVenueFactory()
        offerer = virtual_venue1.managingOfferer
        factories.VenueFactory(managingOfferer=offerer)

        # Cannot add new venue (or change the offerer of an existing one).
        virtual_venue2 = factories.VirtualVenueFactory.build(managingOfferer=offerer)
        with pytest.raises(ApiErrors) as err:
            repository.save(virtual_venue2)
        assert err.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]

        # Cannot change isVirtual on an existing one.
        venue3 = factories.VenueFactory(managingOfferer=offerer)
        venue3.isVirtual = True
        venue3.address = venue3.postalCode = venue3.city = venue3.departementCode = None
        venue3.siret = None
        with pytest.raises(ApiErrors) as err:
            repository.save(venue3)
        assert err.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]

    def test_physical_venue_must_have_an_offerer_address(self):
        with pytest.raises(IntegrityError) as err:
            factories.VenueFactory(offererAddress=None)
        assert "check_physical_venue_has_offerer_address" in str(err.value)


class VenueTimezonePropertyTest:
    def test_europe_paris_is_default_timezone(self):
        venue = factories.VenueFactory(postalCode="75000")

        assert venue.timezone == "Europe/Paris"

    def test_return_timezone_given_venue_departement_code(self):
        venue = factories.VenueFactory(postalCode="97300")

        assert venue.timezone == "America/Cayenne"

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        venue = factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

        assert venue.timezone == "America/Cayenne"


class VenueTimezoneSqlQueryTest:
    def test_europe_paris_is_default_timezone(self):
        factories.VenueFactory(postalCode="75000")
        assert db.session.query(models.Venue).filter_by(timezone="Europe/Paris").count() == 1

    def test_return_timezone_given_venue_departement_code(self):
        factories.VenueFactory(postalCode="97300")
        assert db.session.query(models.Venue).filter_by(timezone="America/Cayenne").count() == 1

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        factories.VirtualVenueFactory(managingOfferer__postalCode="97300")
        assert db.session.query(models.Venue).filter_by(timezone="America/Cayenne").count() == 1


class VenueBannerUrlTest:
    def test_can_set_banner_url_when_none(self, db_session):
        expected_banner_url = "http://example.com/banner_url"
        venue = factories.VenueFactory()

        venue.bannerUrl = expected_banner_url
        repository.save(venue)
        db.session.refresh(venue)

        assert venue.bannerUrl == expected_banner_url
        assert venue._bannerUrl == expected_banner_url

    def test_can_update_existing_banner_url(self, db_session):
        expected_banner_url = "http://example.com/banner_url"
        venue = factories.VenueFactory(bannerUrl="http://example.com/legacy_url")

        venue.bannerUrl = expected_banner_url
        repository.save(venue)
        db.session.refresh(venue)

        assert venue.bannerUrl == expected_banner_url
        assert venue._bannerUrl == expected_banner_url

    @pytest.mark.parametrize(
        "venue_type_code", (type_code for type_code, banners in models.VENUE_TYPE_DEFAULT_BANNERS.items() if banners)
    )
    def test_can_get_category_default_banner_url_when_exists(self, venue_type_code):
        venue = factories.VenueFactory(venueTypeCode=venue_type_code)

        banner_base_url, banner_name = venue.bannerUrl.rsplit("/", 1)
        assert banner_name in models.VENUE_TYPE_DEFAULT_BANNERS[venue_type_code]
        assert banner_base_url == f"{settings.OBJECT_STORAGE_URL}/assets/venue_default_images"

    @pytest.mark.parametrize(
        "venue_type_code",
        (type_code for type_code, banners in models.VENUE_TYPE_DEFAULT_BANNERS.items() if not banners),
    )
    def test_cannot_get_category_default_banner_if_not_available(self, venue_type_code):
        venue = factories.VenueFactory(venueTypeCode=venue_type_code)

        assert venue.bannerUrl is None

    def test_can_get_user_defined_banner_if_exists(self):
        expected_banner_url = "http://example.com/banner_url"
        # no google maps banner
        venue = factories.VenueFactory(bannerUrl=expected_banner_url)

        assert venue.bannerUrl == expected_banner_url
        # with google maps banner
        google_maps_banner_url = "http://example.com/google_maps_banner_url"
        venue = factories.VenueFactory(
            bannerUrl=expected_banner_url,
        )
        factories.GooglePlacesInfoFactory(bannerUrl=google_maps_banner_url, venue=venue)
        assert venue.bannerUrl == expected_banner_url

    def test_can_get_google_maps_banner_url_if_no_user_defined_banner(self):
        google_maps_banner_url = "http://example.com/google_maps_banner_url"
        venue = factories.VenueFactory(bannerUrl=None)
        factories.GooglePlacesInfoFactory(bannerUrl=google_maps_banner_url, venue=venue)

        assert venue.bannerUrl == google_maps_banner_url


class VenueIsEligibleForSearchTest:
    @pytest.mark.parametrize(
        "permanent,active,venue_type_code,is_eligible_for_search",
        [
            (True, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True),
            (True, False, offerers_schemas.VenueTypeCode.BOOKSTORE, False),
            (False, True, offerers_schemas.VenueTypeCode.BOOKSTORE, False),
            (False, False, offerers_schemas.VenueTypeCode.BOOKSTORE, False),
        ],
    )
    def test_legacy_is_eligible_for_search(self, permanent, active, venue_type_code, is_eligible_for_search):
        venue = factories.VenueFactory(
            isVirtual=False,
            managingOfferer__isActive=active,
            isPermanent=permanent,
            venueTypeCode=venue_type_code,
        )
        offers_factories.OfferFactory(venue=venue)
        assert venue.is_eligible_for_search == is_eligible_for_search

    @pytest.mark.parametrize(
        "open_to_public,permanent,validation_status,active,venue_type_code,has_indiv_offer,is_eligible_for_search",
        [
            (True, True, ValidationStatus.VALIDATED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, True),
            (True, True, ValidationStatus.VALIDATED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, False, False),
            (True, False, ValidationStatus.VALIDATED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, True),
            (False, True, ValidationStatus.VALIDATED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
            (False, True, ValidationStatus.VALIDATED, False, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
            (False, False, ValidationStatus.VALIDATED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
            (False, False, ValidationStatus.VALIDATED, False, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
            (True, True, ValidationStatus.NEW, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
            (True, True, ValidationStatus.CLOSED, True, offerers_schemas.VenueTypeCode.BOOKSTORE, True, False),
        ],
    )
    def test_is_eligible_for_search(
        self,
        open_to_public,
        permanent,
        validation_status,
        active,
        venue_type_code,
        has_indiv_offer,
        is_eligible_for_search,
    ):
        venue = factories.VenueFactory(
            isVirtual=False,
            isOpenToPublic=open_to_public,
            managingOfferer__isActive=active,
            managingOfferer__validationStatus=validation_status,
            isPermanent=permanent,
            venueTypeCode=venue_type_code,
        )
        if has_indiv_offer:
            offers_factories.OfferFactory(venue=venue)
        assert venue.is_eligible_for_search == is_eligible_for_search


class VenueHasActiveIndividualOffersTest:
    def test_has_active_individual_offer_property(self):
        venue = factories.VenueFactory()
        offers_factories.EventStockFactory(offer__venue=venue)

        assert venue.hasActiveIndividualOffer == True

    def test_has_not_active_individual_offer_property(self):
        venue = factories.VenueFactory()
        offers_factories.EventStockFactory(offer__venue=venue, offer__isActive=False)

        assert venue.hasActiveIndividualOffer == False


class OffererDepartementCodePropertyTest:
    def test_metropole_postal_code(self):
        offerer = factories.OffererFactory.build(postalCode="75000")

        assert offerer.departementCode == "75"

    def test_drom_postal_code(self):
        offerer = factories.OffererFactory.build(postalCode="97300")

        assert offerer.departementCode == "973"

    def test_guadeloupe_postal_code(self):
        offerer = factories.OffererFactory(postalCode="97100")
        assert offerer.departementCode == "971"

    def test_saint_martin_postal_code(self):
        offerer = factories.OffererFactory(postalCode="97150")
        assert offerer.departementCode == "978"


class OffererDepartementCodeSQLExpressionTest:
    def test_metropole_postal_code(self):
        factories.OffererFactory(postalCode="75000")
        assert db.session.query(models.Offerer).filter_by(departementCode="75").count() == 1

    def test_drom_postal_code(self):
        factories.OffererFactory(postalCode="97300")
        assert db.session.query(models.Offerer).filter_by(departementCode="973").count() == 1

    def test_guadeloupe_postal_code(self):
        factories.OffererFactory(postalCode="97100")
        assert db.session.query(models.Offerer).filter_by(departementCode="971").count() == 1

    def test_saint_martin_postal_code(self):
        factories.OffererFactory(postalCode="97150")
        assert db.session.query(models.Offerer).filter_by(departementCode="978").count() == 1


class OffererIsTopActeurTest:
    def test_is_top_acteur(self):
        offerer = factories.OffererFactory(
            tags=[
                factories.OffererTagFactory(name="test", label="Test"),
                factories.OffererTagFactory(name="top-acteur", label="Top Acteur"),
            ]
        )
        assert offerer.is_top_acteur

    def test_is_not_top_acteur(self):
        offerer = factories.OffererFactory(tags=[factories.OffererTagFactory(name="test", label="Test")])
        assert not offerer.is_top_acteur


class OffererIsTopActeurSQLExpressionTest:
    def test_is_top_acteur(self):
        factories.OffererFactory(
            tags=[
                factories.OffererTagFactory(name="test", label="Test"),
                factories.OffererTagFactory(name="top-acteur", label="Top Acteur"),
            ]
        )
        assert db.session.query(models.Offerer).filter(models.Offerer.is_top_acteur.is_(True)).count() == 1

    def test_is_not_top_acteur(self):
        factories.OffererFactory(tags=[factories.OffererTagFactory(name="test", label="Test")])
        assert db.session.query(models.Offerer).filter(models.Offerer.is_top_acteur.is_(True)).count() == 0


class VenueNApprovedOffersTest:
    def test_venue_n_approved_offers(self):
        venue = factories.VenueFactory()
        for validation_status in offers_models.OfferValidationStatus:
            offers_factories.OfferFactory(venue=venue, validation=validation_status)
        assert venue.nApprovedOffers == 1
        assert venue.has_approved_offers

    def test_venue_n_approved_offers_and_collective_offers(self):
        educational_factories.CollectiveOfferFactory()
        offers_factories.OfferFactory()

        collective_offers = [
            educational_factories.CollectiveOfferFactory(),
            educational_factories.CollectiveOfferFactory(),
        ]
        venue = factories.VenueFactory(collectiveOffers=collective_offers)
        for validation_status in offers_models.OfferValidationStatus:
            offers_factories.OfferFactory(venue=venue, validation=validation_status)
        assert venue.nApprovedOffers == 3
        assert venue.has_approved_offers

    def test_venue_n_approved_offers_zero(self):
        venue = factories.VenueFactory()
        offers_factories.OfferFactory(venue=venue, validation=offers_models.OfferValidationStatus.PENDING)
        educational_factories.CollectiveOfferFactory(venue=venue, validation=offers_models.OfferValidationStatus.DRAFT)
        assert venue.nApprovedOffers == 0
        assert not venue.has_approved_offers


def test_save_user_offerer_raise_api_error_when_not_unique(app):
    user = users_factories.ProFactory.build()
    offerer = factories.OffererFactory()
    factories.UserOffererFactory(user=user, offerer=offerer)

    uo2 = factories.UserOffererFactory.build(user=user, offerer=offerer)
    with pytest.raises(ApiErrors) as error:
        repository.save(uo2)

    assert error.value.errors["global"] == ["Une entrée avec cet identifiant existe déjà dans notre base de données"]


class IsValidatedTest:
    def test_is_validated_property(self):
        offerer = factories.OffererFactory()
        factories.NewUserOffererFactory(offerer=offerer)
        assert offerer.isValidated

    def test_is_validated_property_when_still_offerer_has_validation_token(self):
        offerer = factories.NewOffererFactory()
        factories.UserOffererFactory(offerer=offerer)
        assert not offerer.isValidated


class VenueDmsAdageStatusTest:
    def test_dms_adage_status_when_no_dms_application(self):
        venue = factories.VenueFactory()

        assert venue.dms_adage_status is None

        # hybrid property: also check SQL expression
        assert db.session.query(models.Venue.dms_adage_status).filter_by(id=venue.id).scalar() is None

    def test_dms_adage_status_when_multiple_dms_application(self):
        venue = factories.VenueFactory()
        educational_factories.CollectiveDmsApplicationFactory.create_batch(
            2, venue=venue, lastChangeDate=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )
        latest = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, state="accepte", lastChangeDate=datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        )
        educational_factories.CollectiveDmsApplicationFactory.create_batch(
            2, venue=venue, lastChangeDate=datetime.datetime.utcnow() - datetime.timedelta(days=1)
        )

        assert venue.dms_adage_status == latest.state
        last_collective_dms_application = venue.last_collective_dms_application

        # hybrid property: also check SQL expression
        assert db.session.query(models.Venue.dms_adage_status).filter_by(id=venue.id).scalar() == latest.state
        assert last_collective_dms_application is latest


class CurrentPricingPointTest:
    def _load_venue(self, venue_id) -> models.Venue:
        return (
            db.session.query(models.Venue)
            .filter_by(id=venue_id)
            .options(
                sa_orm.joinedload(models.Venue.pricing_point_links).joinedload(
                    models.VenuePricingPointLink.pricingPoint
                )
            )
            .one()
        )

    def test_no_pricing_point(self):
        venue = factories.VenueWithoutSiretFactory()

        venue_with_joinedload = self._load_venue(venue.id)

        with assert_num_queries(0):
            assert venue_with_joinedload.current_pricing_point_link is None
            assert venue_with_joinedload.current_pricing_point is None

    def test_pricing_point(self):
        venue = factories.VenueWithoutSiretFactory()
        now = datetime.datetime.utcnow()
        factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=factories.VenueFactory(managingOfferer=venue.managingOfferer, name="former"),
            timespan=[now - datetime.timedelta(days=7), now - datetime.timedelta(days=1)],
        )
        link = factories.VenuePricingPointLinkFactory(
            venue=venue,
            pricingPoint=factories.VenueFactory(managingOfferer=venue.managingOfferer, name="current"),
            timespan=[now - datetime.timedelta(days=1), None],
        )

        venue_with_joinedload = self._load_venue(venue.id)

        with assert_num_queries(0):
            assert venue_with_joinedload.current_pricing_point_link == link
            assert venue_with_joinedload.current_pricing_point is not None
            assert venue_with_joinedload.current_pricing_point.name == "current"


class CurrentBankAccountTest:
    def _load_venue(self, venue_id) -> models.Venue:
        return (
            db.session.query(models.Venue)
            .filter_by(id=venue_id)
            .options(
                sa_orm.joinedload(models.Venue.bankAccountLinks).joinedload(models.VenueBankAccountLink.bankAccount)
            )
            .one()
        )

    def test_no_bank_account(self):
        venue = factories.VenueWithoutSiretFactory()

        venue_with_joinedload = self._load_venue(venue.id)

        with assert_num_queries(0):
            assert venue_with_joinedload.current_bank_account_link is None

    def test_bank_account_link(self):
        venue = factories.VenueWithoutSiretFactory()
        now = datetime.datetime.utcnow()
        factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=finance_factories.BankAccountFactory(offererId=venue.managingOffererId, label="former"),
            timespan=[now - datetime.timedelta(days=7), now - datetime.timedelta(days=1)],
        )
        link = factories.VenueBankAccountLinkFactory(
            venue=venue,
            bankAccount=finance_factories.BankAccountFactory(offererId=venue.managingOffererId, label="current"),
            timespan=[now - datetime.timedelta(days=1), None],
        )

        venue_with_joinedload = self._load_venue(venue.id)

        with assert_num_queries(0):
            assert venue_with_joinedload.current_bank_account_link == link
            assert venue_with_joinedload.current_bank_account_link.bankAccount.label == "current"


class VenueBankAccountLinkTest:
    def test_venue_and_bank_account_cant_overlap(self):
        venue = factories.VenueFactory()
        bank_account = finance_factories.BankAccountFactory()

        with pytest.raises(IntegrityError):
            factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)
            factories.VenueBankAccountLinkFactory(venue=venue, bankAccount=bank_account)


class OffererConfidenceRuleTest:
    def test_cannot_set_both_offerer_and_venue(self):
        venue = factories.VenueFactory()

        with pytest.raises(IntegrityError):
            factories.ManualReviewOffererConfidenceRuleFactory(offerer=venue.managingOfferer, venue=venue)

    def test_cannot_set_no_offerer_no_venue(self):
        with pytest.raises(IntegrityError):
            factories.OffererConfidenceRuleFactory(confidenceLevel=models.OffererConfidenceLevel.WHITELIST)

    def test_strategy_cannot_be_null(self):
        with pytest.raises(IntegrityError):
            factories.OffererConfidenceRuleFactory(offerer=factories.OffererFactory(), confidenceLevel=None)


class OffererAddressTest:
    def test_offerer_address_isLinkedToVenue_property_should_be_true(self):
        offererAddress = factories.OffererAddressFactory()
        factories.VenueFactory(offererAddress=offererAddress)
        assert offererAddress.isLinkedToVenue is True

    def test_offerers_address_is_notLinkedToVenue_property_should_be_false(self):
        offererAddress = factories.OffererAddressFactory()
        assert offererAddress.isLinkedToVenue is False

    def test_offerers_address_isLinkedToVenue_expression_should_be_false(self):
        offererAddress = factories.OffererAddressFactory()
        assert db.session.query(models.OffererAddress).filter_by(id=offererAddress.id).one().isLinkedToVenue is False
        assert db.session.query(models.OffererAddress).filter(models.OffererAddress.isLinkedToVenue == False).one()

    def test_offerers_address_isLinkedToVenue_expression_should_be_true(self):
        offererAddress = factories.OffererAddressFactory()
        factories.VenueFactory(offererAddress=offererAddress)
        assert db.session.query(models.OffererAddress).filter(models.OffererAddress.isLinkedToVenue == True).one()


class OffererRid7Test:
    def test_rid7_when_offerer_is_caledonian(self):
        offerer = factories.OffererFactory(siren="NC1234567")
        assert offerer.rid7 == "1234567"

    def test_rid7_when_offerer_is_not_caledonian(self):
        offerer = factories.OffererFactory()
        assert offerer.rid7 is None


class OffererIsCaledonianTest:
    def test_offerer_with_rid7_is_caledonian(self):
        offerer = factories.CaledonianOffererFactory(siren="NC1234567")
        assert offerer.is_caledonian

    def test_offerer_with_siren_is_caledonian(self):
        offerer = factories.CaledonianOffererFactory(siren="123456789", postalCode="98800")
        assert offerer.is_caledonian

    def test_offerer_is_not_caledonian(self):
        offerer = factories.OffererFactory()
        assert not offerer.is_caledonian


class OffererIdentifierTest:
    def test_identifier_is_siren(self):
        offerer = factories.OffererFactory()
        assert offerer.identifier_name == "SIREN"
        assert offerer.identifier == offerer.siren

    def test_identifier_is_rid7(self):
        offerer = factories.CaledonianOffererFactory()
        assert offerer.identifier_name == "RID7"
        assert offerer.identifier == offerer.rid7


class VenueRidetTest:
    def test_ridet_when_venue_is_caledonian(self):
        offerer = factories.CaledonianVenueFactory(siret="NC1234567001XX")
        assert offerer.ridet == "1234567001"

    def test_ridet_when_venue_is_not_caledonian(self):
        offerer = factories.VenueFactory()
        assert offerer.ridet is None


class VenueIdentifierTest:
    def test_identifier_is_siret(self):
        venue = factories.VenueFactory()
        assert venue.identifier_name == "SIRET"
        assert venue.identifier == venue.siret

    def test_identifier_is_rid7(self):
        venue = factories.CaledonianVenueFactory()
        assert venue.identifier_name == "RIDET"
        assert venue.identifier == venue.ridet


class VenueIsCaledonianTest:
    def test_venue_is_caledonian(self):
        venue = factories.CaledonianVenueFactory()
        assert venue.is_caledonian

    def test_virtual_venue_is_caledonian(self):
        offerer = factories.CaledonianOffererFactory(siren="123456789", postalCode="98800")
        venue = factories.VirtualVenueFactory(managingOfferer=offerer)
        assert venue.is_caledonian

    def test_offerer_is_not_caledonian(self):
        venue = factories.VenueFactory()
        assert not venue.is_caledonian


class VenueHasPartnerPageTest:
    @pytest.mark.parametrize(
        "active_offerer,permanent_venue,virtual_venue,at_least_one_offer,has_partner_page",
        [
            (False, True, False, True, False),
            (True, False, False, True, False),
            (True, True, True, True, False),
            (True, True, False, False, False),
            (True, True, False, True, True),
        ],
    )
    def test_has_partner_page(
        self, active_offerer, permanent_venue, virtual_venue, at_least_one_offer, has_partner_page
    ):
        offerer = factories.OffererFactory(isActive=active_offerer)
        if virtual_venue:
            venue = factories.VirtualVenueFactory(managingOfferer=offerer, isPermanent=permanent_venue)
        else:
            venue = factories.VenueFactory(managingOfferer=offerer, isPermanent=permanent_venue)
        if at_least_one_offer:
            offers_factories.OfferFactory(venue=venue)
        assert venue.has_partner_page is has_partner_page

    def test_has_partner_page_isolation(self):
        offerer_1 = factories.OffererFactory(isActive=True)
        offerer_2 = factories.OffererFactory(isActive=True)
        partner_page_venue = factories.VenueFactory(managingOfferer=offerer_2, isPermanent=True)
        venue = factories.VenueFactory(managingOfferer=offerer_1, isPermanent=False)
        offers_factories.OfferFactory(venue=partner_page_venue)

        assert venue.has_partner_page is False
        assert partner_page_venue.has_partner_page is True
        assert db.session.query(models.Venue).filter(models.Venue.has_partner_page == False).all() == [venue]
        assert db.session.query(models.Venue).filter(models.Venue.has_partner_page == True).all() == [
            partner_page_venue
        ]

    def test_closed_offerer_has_no_partner_page(self):
        offerer = factories.ClosedOffererFactory()
        venue = factories.VenueFactory(managingOfferer=offerer, isPermanent=True)
        offers_factories.OfferFactory(venue=venue)

        assert venue.has_partner_page is False
        assert db.session.query(models.Venue).filter(models.Venue.has_partner_page == False).all() == [venue]
        assert db.session.query(models.Venue).filter(models.Venue.has_partner_page == True).count() == 0
