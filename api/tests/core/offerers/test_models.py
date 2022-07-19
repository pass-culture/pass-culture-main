from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.educational import factories as educational_factories
import pcapi.core.finance.factories as finance_factories
import pcapi.core.finance.models as finance_models
from pcapi.core.offerers import factories
from pcapi.core.offerers import models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


pytestmark = pytest.mark.usefixtures("db_session")


class VenueModelConstraintsTest:
    def test_virtual_venue_cannot_have_address(self):
        venue = factories.VirtualVenueFactory()

        with pytest.raises(IntegrityError) as err:
            venue.address = "1 test address"
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_virtual_venue_cannot_have_siret(self):
        venue = factories.VirtualVenueFactory()
        with pytest.raises(IntegrityError) as err:
            venue.siret = "siret"
            db.session.add(venue)
            db.session.commit()
        assert "check_has_siret_xor_comment_xor_isVirtual" in str(err.value)

    def test_non_virtual_with_siret_can_have_null_address(self):
        # The following statement should not fail.
        factories.VenueFactory(siret="siret", address=None)

    def test_non_virtual_with_siret_must_have_postal_code_and_city(self):
        venue = factories.VenueFactory(siret="siret")
        venue.postal_code = None
        venue.city = None
        with pytest.raises(IntegrityError) as err:
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_non_virtual_without_siret_must_have_full_address(self):
        venue = factories.VenueFactory(siret=None, comment="no siret, it's ok")
        venue.address = None
        venue.postal_code = None
        venue.city = None
        with pytest.raises(IntegrityError) as err:
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_non_virtual_without_siret_must_have_comment(self):
        venue = factories.VenueFactory(siret=None, comment="no siret, it's ok")
        with pytest.raises(IntegrityError) as err:
            venue.comment = None
            db.session.add(venue)
            db.session.commit()
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
        assert models.Venue.query.filter_by(timezone="Europe/Paris").count() == 1

    def test_return_timezone_given_venue_departement_code(self):
        factories.VenueFactory(postalCode="97300")
        assert models.Venue.query.filter_by(timezone="America/Cayenne").count() == 1

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        factories.VirtualVenueFactory(managingOfferer__postalCode="97300")
        assert models.Venue.query.filter_by(timezone="America/Cayenne").count() == 1


class OffererDepartementCodePropertyTest:
    def test_metropole_postal_code(self):
        offerer = factories.OffererFactory.build(postalCode="75000")

        assert offerer.departementCode == "75"

    def test_drom_postal_code(self):
        offerer = factories.OffererFactory.build(postalCode="97300")

        assert offerer.departementCode == "973"


class OffererDepartementCodeSQLExpressionTest:
    def test_metropole_postal_code(self):
        factories.OffererFactory(postalCode="75000")
        assert models.Offerer.query.filter_by(departementCode="75").count() == 1

    def test_drom_postal_code(self):
        factories.OffererFactory(postalCode="97300")
        assert models.Offerer.query.filter_by(departementCode="973").count() == 1


class VenueNApprovedOffersTest:
    def test_venue_n_approved_offers(self):
        venue = factories.VenueFactory()
        for validation_status in offers_models.OfferValidationStatus:
            offers_factories.OfferFactory(venue=venue, validation=validation_status)
        assert venue.nApprovedOffers == 1

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


class OffererLegalCategoryTest:
    @patch("pcapi.core.offerers.models.get_offerer_legal_category")
    def test_offerer_legal_category_called_many_times(self, mocked_get_offerer_legal_category):
        info = {
            "legal_category_code": "5202",
            "legal_category_label": "Société en nom collectif",
        }
        mocked_get_offerer_legal_category.return_value = info
        offerer = factories.OffererFactory.build()

        assert offerer.legal_category == info
        assert offerer.legal_category == info
        assert offerer.legal_category == info
        assert mocked_get_offerer_legal_category.call_count == 1


def test_save_user_offerer_raise_api_error_when_not_unique(app):
    user = users_factories.ProFactory.build()
    offerer = factories.OffererFactory()
    factories.UserOffererFactory(user=user, offerer=offerer)

    uo2 = factories.UserOffererFactory.build(user=user, offerer=offerer)
    with pytest.raises(ApiErrors) as error:
        repository.save(uo2)

    assert error.value.errors["global"] == ["Une entrée avec cet identifiant existe déjà dans notre base de données"]


class OffererBankInformationTest:
    def test_bic_property_returns_bank_information_bic_when_offerer_has_bank_information(self):
        offerer = factories.OffererFactory()
        finance_factories.BankInformationFactory(offerer=offerer, bic="BDFEFR2LCCB")
        assert offerer.bic == "BDFEFR2LCCB"

    def test_bic_property_returns_none_when_offerer_does_not_have_bank_information(self):
        offerer = factories.OffererFactory()
        assert offerer.bic is None

    def test_iban_property_returns_bank_information_iban_when_offerer_has_bank_information(self):
        offerer = factories.OffererFactory()
        finance_factories.BankInformationFactory(offerer=offerer, iban="FR7630007000111234567890144")
        assert offerer.iban == "FR7630007000111234567890144"

    def test_iban_property_returns_none_when_offerer_does_not_have_bank_information(self):
        offerer = factories.OffererFactory()
        assert offerer.iban is None

    def test_demarchesSimplifieesApplicationId_returns_id_if_status_is_draft(self):
        offerer = factories.OffererFactory()
        finance_factories.BankInformationFactory(
            offerer=offerer,
            applicationId=12345,
            status=finance_models.BankInformationStatus.DRAFT,
        )
        assert offerer.demarchesSimplifieesApplicationId == 12345

    def test_demarchesSimplifieesApplicationId_returns_none_if_status_is_rejected(self):
        offerer = factories.OffererFactory()
        info = finance_factories.BankInformationFactory(
            offerer=offerer,
            applicationId=12345,
            status=finance_models.BankInformationStatus.REJECTED,
        )
        offerer = info.offerer
        assert offerer.demarchesSimplifieesApplicationId is None


class IsValidatedTest:
    def test_is_validated_property(self):
        offerer = factories.OffererFactory()
        factories.UserOffererFactory(offerer=offerer, validationToken="token")
        assert offerer.isValidated

    def test_is_validated_property_when_still_offerer_has_validation_token(self):
        offerer = factories.OffererFactory(validationToken="token")
        factories.UserOffererFactory(offerer=offerer)
        assert not offerer.isValidated


class HasPendingBankInformationApplicationTest:
    def test_no_application(self):
        venue = factories.VenueFactory()

        assert venue.hasPendingBankInformationApplication is False

    def test_draft_application(self):
        venue = factories.VenueFactory()
        finance_factories.BankInformationFactory(
            venue=venue, status=finance_models.BankInformationStatus.DRAFT, bic=None, iban=None
        )

        assert venue.hasPendingBankInformationApplication is True

    def test_accepted_application(self):
        venue = factories.VenueFactory()
        finance_factories.BankInformationFactory(
            venue=venue,
            status=finance_models.BankInformationStatus.ACCEPTED,
        )

        assert venue.hasPendingBankInformationApplication is False

    def test_rejected_application(self):
        venue = factories.VenueFactory()
        finance_factories.BankInformationFactory(
            venue=venue, status=finance_models.BankInformationStatus.REJECTED, bic=None, iban=None
        )

        assert venue.hasPendingBankInformationApplication is False
