from unittest.mock import patch

import pytest
from sqlalchemy.exc import IntegrityError

from pcapi.core.offerers import factories
from pcapi.core.offerers import models
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.users import factories as users_factories
from pcapi.models import db
from pcapi.models.api_errors import ApiErrors
from pcapi.repository import repository


@pytest.mark.usefixtures("db_session")
class VenueModelConstraintsTest:
    def test_virtual_venue_cannot_have_address(self):
        venue = offers_factories.VirtualVenueFactory()

        with pytest.raises(IntegrityError) as err:
            venue.address = "1 test address"
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_virtual_venue_cannot_have_siret(self):
        venue = offers_factories.VirtualVenueFactory()
        with pytest.raises(IntegrityError) as err:
            venue.siret = "siret"
            db.session.add(venue)
            db.session.commit()
        assert "check_has_siret_xor_comment_xor_isVirtual" in str(err.value)

    def test_non_virtual_with_siret_can_have_null_address(self):
        # The following statement should not fail.
        offers_factories.VenueFactory(siret="siret", address=None)

    def test_non_virtual_with_siret_must_have_postal_code_and_city(self):
        venue = offers_factories.VenueFactory(siret="siret")
        venue.postal_code = None
        venue.city = None
        with pytest.raises(IntegrityError) as err:
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_non_virtual_without_siret_must_have_full_address(self):
        venue = offers_factories.VenueFactory(siret=None, comment="no siret, it's ok")
        venue.address = None
        venue.postal_code = None
        venue.city = None
        with pytest.raises(IntegrityError) as err:
            db.session.add(venue)
            db.session.commit()
        assert "check_is_virtual_xor_has_address" in str(err.value)

    def test_non_virtual_without_siret_must_have_comment(self):
        venue = offers_factories.VenueFactory(siret=None, comment="no siret, it's ok")
        with pytest.raises(IntegrityError) as err:
            venue.comment = None
            db.session.add(venue)
            db.session.commit()
        assert "check_has_siret_xor_comment_xor_isVirtual" in str(err.value)

    def test_at_most_one_virtual_venue_per_offerer(self):
        virtual_venue1 = offers_factories.VirtualVenueFactory()
        offerer = virtual_venue1.managingOfferer
        offers_factories.VenueFactory(managingOfferer=offerer)

        # Cannot add new venue (or change the offerer of an existing one).
        virtual_venue2 = offers_factories.VirtualVenueFactory.build(managingOfferer=offerer)
        with pytest.raises(ApiErrors) as err:
            repository.save(virtual_venue2)
        assert err.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]

        # Cannot change isVirtual on an existing one.
        venue3 = offers_factories.VenueFactory(managingOfferer=offerer)
        venue3.isVirtual = True
        venue3.address = venue3.postalCode = venue3.city = venue3.departementCode = None
        venue3.siret = None
        with pytest.raises(ApiErrors) as err:
            repository.save(venue3)
        assert err.value.errors["isVirtual"] == ["Un lieu pour les offres numériques existe déjà pour cette structure"]


@pytest.mark.usefixtures("db_session")
class VenueTimezonePropertyTest:
    def test_europe_paris_is_default_timezone(self):
        venue = offers_factories.VenueFactory(postalCode="75000")

        assert venue.timezone == "Europe/Paris"

    def test_return_timezone_given_venue_departement_code(self):
        venue = offers_factories.VenueFactory(postalCode="97300")

        assert venue.timezone == "America/Cayenne"

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        venue = offers_factories.VirtualVenueFactory(managingOfferer__postalCode="97300")

        assert venue.timezone == "America/Cayenne"


@pytest.mark.usefixtures("db_session")
class VenueTimezoneSqlQueryTest:
    def test_europe_paris_is_default_timezone(self):
        offers_factories.VenueFactory(postalCode="75000")
        assert models.Venue.query.filter_by(timezone="Europe/Paris").count() == 1

    def test_return_timezone_given_venue_departement_code(self):
        offers_factories.VenueFactory(postalCode="97300")
        assert models.Venue.query.filter_by(timezone="America/Cayenne").count() == 1

    def test_return_managing_offerer_timezone_when_venue_is_virtual(self):
        offers_factories.VirtualVenueFactory(managingOfferer__postalCode="97300")
        assert models.Venue.query.filter_by(timezone="America/Cayenne").count() == 1


class OffererDepartementCodePropertyTest:
    def test_metropole_postal_code(self):
        offerer = factories.OffererFactory.build(postalCode="75000")

        assert offerer.departementCode == "75"

    def test_drom_postal_code(self):
        offerer = offers_factories.OffererFactory.build(postalCode="97300")

        assert offerer.departementCode == "973"


@pytest.mark.usefixtures("db_session")
class OffererDepartementCodeSQLExpressionTest:
    def test_metropole_postal_code(self):
        factories.OffererFactory(postalCode="75000")
        assert models.Offerer.query.filter_by(departementCode="75").count() == 1

    def test_drom_postal_code(self):
        factories.OffererFactory(postalCode="97300")
        assert models.Offerer.query.filter_by(departementCode="973").count() == 1


@pytest.mark.usefixtures("db_session")
class VenueNApprovedOffersTest:
    def test_venue_n_approved_offers(self):
        venue = factories.VenueFactory()
        for validation_status in offers_models.OfferValidationStatus:
            offers_factories.OfferFactory(venue=venue, validation=validation_status)
        assert venue.nApprovedOffers == 1


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


class OffererGrantAccessTest:
    def test_grant_access_to_offerer_to_given_pro(self):
        # Given
        offerer = factories.OffererFactory.build()
        user = users_factories.UserFactory.build()

        # When
        created_user_offerer = offerer.grant_access(user)

        # Then
        assert created_user_offerer.user == user
        assert created_user_offerer.offerer == offerer
        assert not user.has_pro_role

    def test_do_nothing_when_no_user_provided(self):
        # Given
        offerer = factories.OffererFactory.build()

        # When
        created_user_offerer = offerer.grant_access(None)

        # Then
        assert created_user_offerer is None


@pytest.mark.usefixtures("db_session")
class VenueCriterionTest:
    def test_unique_venue_criterion(self):
        venue = factories.VenueFactory()
        criterion = offers_factories.CriterionFactory()
        factories.VenueCriterionFactory(venue=venue, criterion=criterion)
        with pytest.raises(IntegrityError):
            factories.VenueCriterionFactory(venue=venue, criterion=criterion)
