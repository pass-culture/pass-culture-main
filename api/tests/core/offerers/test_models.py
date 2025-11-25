import datetime

import pytest
import sqlalchemy.orm as sa_orm
from sqlalchemy.exc import IntegrityError

import pcapi.core.finance.factories as finance_factories
import pcapi.core.offerers.schemas as offerers_schemas
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi import settings
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import constants
from pcapi.core.offerers import factories
from pcapi.core.offerers import models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.utils import date as date_utils


pytestmark = pytest.mark.usefixtures("db_session")


class VenueModelConstraintsTest:
    def test_venue_without_siret_must_have_comment(self):
        venue = factories.VenueWithoutSiretFactory()
        with pytest.raises(IntegrityError) as err:
            venue.comment = None
            db.session.add(venue)
            db.session.flush()
        assert "check_has_siret_or_comment" in str(err.value)

    def test_physical_venue_must_have_an_offerer_address(self):
        with pytest.raises(IntegrityError) as err:
            factories.VenueFactory(offererAddress=None)
        assert """null value in column "offererAddressId" of relation "venue" violates not-null constraint""" in str(
            err.value
        )


class VenueBannerUrlTest:
    def test_can_set_banner_url_when_none(self, db_session):
        expected_banner_url = "http://example.com/banner_url"
        venue = factories.VenueFactory()

        venue.bannerUrl = expected_banner_url
        db.session.add(venue)
        db.session.commit()
        db.session.refresh(venue)

        assert venue.bannerUrl == expected_banner_url
        assert venue._bannerUrl == expected_banner_url

    def test_can_update_existing_banner_url(self, db_session):
        expected_banner_url = "http://example.com/banner_url"
        venue = factories.VenueFactory(bannerUrl="http://example.com/legacy_url")

        venue.bannerUrl = expected_banner_url
        db.session.add(venue)
        db.session.commit()

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
            isOpenToPublic=open_to_public,
            managingOfferer__isActive=active,
            managingOfferer__validationStatus=validation_status,
            isPermanent=permanent,
            venueTypeCode=venue_type_code,
        )
        if has_indiv_offer:
            offers_factories.OfferFactory(venue=venue)
        assert venue.is_eligible_for_search == is_eligible_for_search

        def test_caledonian_venue_is_eligible_for_search(self):
            venue = factories.CaledonianVenueFactory(venueTypeCode=offerers_schemas.VenueTypeCode.BOOKSTORE)
            offers_factories.OfferFactory(venue=venue)

            assert venue.is_eligible_for_search is False


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
                factories.OffererTagFactory(name=constants.TOP_ACTEUR_TAG_NAME, label="Top Acteur"),
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
                factories.OffererTagFactory(name=constants.TOP_ACTEUR_TAG_NAME, label="Top Acteur"),
            ]
        )
        assert db.session.query(models.Offerer).filter(models.Offerer.is_top_acteur.is_(True)).count() == 1

    def test_is_not_top_acteur(self):
        factories.OffererFactory(tags=[factories.OffererTagFactory(name="test", label="Test")])
        assert db.session.query(models.Offerer).filter(models.Offerer.is_top_acteur.is_(True)).count() == 0


class OffererDepartmentCodesTest:
    def test_offerer_department_codes(self):
        offerer = factories.OffererFactory()
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="11")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="22")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="33")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="11")
        deleted_venue = factories.VenueFactory(managingOfferer=offerer, offererAddress__address__departmentCode="44")
        deleted_venue.isSoftDeleted = True
        db.session.flush()

        offerer = (
            db.session.query(models.Offerer)
            .filter_by(id=offerer.id)
            .options(
                sa_orm.with_expression(models.Offerer.department_codes, models.Offerer.department_codes_expression())
            )
            .one()
        )

        assert sorted(offerer.department_codes) == ["11", "22", "33"]


class OffererCitiesTest:
    def test_offerer_cities(self):
        offerer = factories.OffererFactory()
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Marseille")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Lyon")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Toulouse")
        factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Lyon")
        deleted_venue = factories.VenueFactory(managingOfferer=offerer, offererAddress__address__city="Nice")
        deleted_venue.isSoftDeleted = True
        db.session.flush()

        offerer = (
            db.session.query(models.Offerer)
            .filter_by(id=offerer.id)
            .options(sa_orm.with_expression(models.Offerer.cities, models.Offerer.cities_expression()))
            .one()
        )

        assert sorted(offerer.cities) == ["Lyon", "Marseille", "Toulouse"]


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
            2, venue=venue, lastChangeDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1)
        )
        latest = educational_factories.CollectiveDmsApplicationFactory(
            venue=venue, state="accepte", lastChangeDate=date_utils.get_naive_utc_now() - datetime.timedelta(hours=1)
        )
        educational_factories.CollectiveDmsApplicationFactory.create_batch(
            2, venue=venue, lastChangeDate=date_utils.get_naive_utc_now() - datetime.timedelta(days=1)
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
        now = date_utils.get_naive_utc_now()
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
        now = date_utils.get_naive_utc_now()
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
        offerer_address = factories.OffererAddressFactory()
        factories.VenueFactory(offererAddress=offerer_address)
        assert offerer_address.isLinkedToVenue is True

    def test_offerers_address_is_notLinkedToVenue_property_should_be_false(self):
        offerer_address = factories.OffererAddressFactory()
        assert offerer_address.isLinkedToVenue is False

    def test_offerers_address_isLinkedToVenue_expression_should_be_false(self):
        offerer_address = factories.OffererAddressFactory()
        assert db.session.query(models.OffererAddress).filter_by(id=offerer_address.id).one().isLinkedToVenue is False
        assert db.session.query(models.OffererAddress).filter(models.OffererAddress.isLinkedToVenue == False).one()

    def test_offerers_address_isLinkedToVenue_expression_should_be_true(self):
        offerer_address = factories.OffererAddressFactory()
        factories.VenueFactory(offererAddress=offerer_address)
        assert db.session.query(models.OffererAddress).filter(models.OffererAddress.isLinkedToVenue == True).one()

    def test_unique_constraint_on_legacy_offerer_address_raises(self):
        offerer_address = factories.OffererAddressFactory()

        with pytest.raises(IntegrityError):
            factories.OffererAddressFactory(
                offerer=offerer_address.offerer,
                address=offerer_address.address,
                label=offerer_address.label,
            )

    def test_unique_constraint_on_legacy_offerer_address_does_not_raise_when_label_is_null(self):
        offerer_address = factories.OffererAddressFactory(label=None)

        factories.OffererAddressFactory(
            offerer=offerer_address.offerer,
            address=offerer_address.address,
            label=None,
        )

    def test_unique_constraint_on_offerer_address_raises_when_label_is_null(self):
        offerer_address = factories.VenueLocationFactory(label=None)

        with pytest.raises(IntegrityError):
            factories.VenueLocationFactory(
                offerer=offerer_address.offerer,
                address=offerer_address.address,
                label=None,
                venue=offerer_address.venue,
            )

    def test_unique_constraint_on_offerer_address_raises_when_label_is_filled(self):
        offerer_address = factories.VenueLocationFactory()

        with pytest.raises(IntegrityError):
            factories.VenueLocationFactory(
                offerer=offerer_address.offerer,
                address=offerer_address.address,
                label=offerer_address.label,
                venue=offerer_address.venue,
            )

    def test_unique_constraint_on_offerer_address_validates(self):
        offerer_address = factories.VenueLocationFactory()

        factories.OffererAddressFactory(
            offerer=offerer_address.offerer,
            address=offerer_address.address,
            label="Other label",
            type=models.LocationType.VENUE_LOCATION,
            venue=offerer_address.venue,
        )

        factories.OffererAddressFactory(
            offerer=offerer_address.offerer,
            address=offerer_address.address,
            label=offerer_address.label,
            type=models.LocationType.OFFER_LOCATION,
            venue=offerer_address.venue,
        )

        factories.OffererAddressFactory(
            offerer=offerer_address.offerer,
            address=offerer_address.address,
            label=offerer_address.label,
            type=models.LocationType.VENUE_LOCATION,
            venue=factories.VenueFactory(managingOfferer=offerer_address.offerer),
        )


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
        assert db.session.query(models.Offerer).filter(models.Offerer.is_caledonian).one() == offerer

    def test_offerer_is_not_caledonian(self):
        offerer = factories.OffererFactory()
        assert not offerer.is_caledonian
        assert db.session.query(models.Offerer).filter(models.Offerer.is_caledonian).count() == 0


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

    def test_venue_without_ridet_is_caledonian(self):
        venue = factories.CaledonianVenueWithoutRidetFactory()
        assert venue.is_caledonian

    def test_venue_is_not_caledonian(self):
        venue = factories.VenueFactory()
        assert not venue.is_caledonian

    def test_venue_without_siret_is_not_caledonian(self):
        venue = factories.VenueWithoutSiretFactory()
        assert not venue.is_caledonian


class VenueHasPartnerPageTest:
    @pytest.mark.parametrize(
        "active_offerer,permanent_venue,at_least_one_offer,has_partner_page",
        [
            (False, True, True, False),
            (True, False, True, False),
            (True, True, False, False),
            (True, True, True, True),
        ],
    )
    def test_has_partner_page(self, active_offerer, permanent_venue, at_least_one_offer, has_partner_page):
        offerer = factories.OffererFactory(isActive=active_offerer)
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
