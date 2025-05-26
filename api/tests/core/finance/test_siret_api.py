import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import siret_api
from pcapi.core.history import models as history_models
from pcapi.models import db


class DeleteSiretTest:
    @pytest.mark.usefixtures("clean_database")
    def test_basics(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        dependent_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, pricing_point=venue)
        initial_statuses = set(models.PricingStatus)
        for status in initial_statuses:
            finance_event = factories.FinanceEventFactory(venue=venue)
            factories.PricingFactory(
                booking=finance_event.booking, pricingPoint=venue, status=status, event=finance_event
            )
        assert db.session.query(models.Pricing.id).count() == 4
        old_siret = venue.siret

        siret_api.remove_siret(venue, comment="no SIRET because reasons")

        assert venue.siret is None
        assert venue.comment == "no SIRET because reasons"
        assert venue.current_pricing_point_id is None
        assert dependent_venue.current_pricing_point_id is None
        assert db.session.query(models.Pricing.id).count() == 3
        left_statuses = {status for (status,) in db.session.query(models.Pricing).with_entities(models.Pricing.status)}
        assert left_statuses == initial_statuses - {models.PricingStatus.VALIDATED}

        actions = db.session.query(history_models.ActionHistory).all()
        assert len(actions) == 2
        for action in actions:
            assert action.actionType == history_models.ActionType.INFO_MODIFIED
            assert action.offererId == venue.managingOffererId
            assert action.venueId in (venue.id, dependent_venue.id)
            assert action.extraData["modified_info"]["pricingPointSiret"] == {"old_info": old_siret, "new_info": None}

    @pytest.mark.usefixtures("clean_database")
    def test_with_new_pricing_point(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        dependent_venue = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer, pricing_point=venue)
        initial_statuses = set(models.PricingStatus)
        finance_events = {}
        for status in initial_statuses:
            finance_event = factories.FinanceEventFactory(venue=venue, status=models.FinanceEventStatus.PENDING)
            assert finance_event.pricingPoint == venue
            finance_events[status] = finance_event
            factories.PricingFactory(
                booking=finance_event.booking, pricingPoint=venue, status=status, event=finance_event
            )

        assert db.session.query(models.Pricing.id).count() == 4
        new_pricing_point = offerers_factories.VenueFactory(managingOfferer=venue.managingOfferer)
        old_siret = venue.siret

        siret_api.remove_siret(venue, comment="no SIRET because reasons", new_pricing_point_id=new_pricing_point.id)

        db.session.expire_all()

        assert venue.siret is None
        assert venue.comment == "no SIRET because reasons"
        assert venue.current_pricing_point_id == new_pricing_point.id
        assert dependent_venue.current_pricing_point_id is None
        assert db.session.query(models.Pricing.id).count() == 3
        left_statuses = {status for (status,) in db.session.query(models.Pricing).with_entities(models.Pricing.status)}
        assert left_statuses == initial_statuses - {models.PricingStatus.VALIDATED}

        assert finance_events[models.PricingStatus.VALIDATED].status == models.FinanceEventStatus.READY
        assert finance_events[models.PricingStatus.VALIDATED].pricingPoint == new_pricing_point

        actions = db.session.query(history_models.ActionHistory).order_by(history_models.ActionHistory.id).all()
        assert len(actions) == 2
        assert actions[0].actionType == history_models.ActionType.INFO_MODIFIED
        assert actions[0].offererId == venue.managingOffererId
        assert actions[0].venueId == venue.id
        assert actions[0].extraData["modified_info"]["pricingPointSiret"] == {
            "old_info": old_siret,
            "new_info": new_pricing_point.siret,
        }
        assert actions[1].actionType == history_models.ActionType.INFO_MODIFIED
        assert actions[1].offererId == dependent_venue.managingOffererId
        assert actions[1].venueId == dependent_venue.id
        assert actions[1].extraData["modified_info"]["pricingPointSiret"] == {"old_info": old_siret, "new_info": None}

    @pytest.mark.usefixtures("clean_database")
    def test_revenue_check(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        user = users_factories.RichBeneficiaryFactory()
        bookings_factories.UsedBookingFactory(
            amount=10_000,
            user=user,
            stock__offer__venue=venue,
        )

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx")
        assert "Ce partenaire culturel a un chiffre d'affaires de l'année élevé" in str(err.value)
        assert venue.siret is not None

        siret_api.remove_siret(
            venue,
            comment="xxx",
            override_revenue_check=True,  # <-- override check
        )
        assert venue.siret is None

    @pytest.mark.usefixtures("clean_database")
    def test_refuse_if_new_pricing_point_does_not_exist(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx", new_pricing_point_id=venue.id + 1000)
        assert (
            str(err.value)
            == "Le nouveau point de valorisation doit être un partenaire culturel avec SIRET sur la même entité juridique"
        )

    @pytest.mark.usefixtures("clean_database")
    def test_refuse_if_new_pricing_point_has_no_siret(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        new_pricing_point = offerers_factories.VenueWithoutSiretFactory(managingOffererId=venue.managingOffererId)

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx", new_pricing_point_id=new_pricing_point.id)
        assert (
            str(err.value)
            == "Le nouveau point de valorisation doit être un partenaire culturel avec SIRET sur la même entité juridique"
        )

    @pytest.mark.usefixtures("clean_database")
    def test_refuse_if_new_pricing_point_is_managed_by_another_offerer(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        new_pricing_point = offerers_factories.VenueFactory(pricing_point="self")

        with pytest.raises(siret_api.CheckError) as err:
            siret_api.remove_siret(venue, comment="xxx", new_pricing_point_id=new_pricing_point.id)
        assert (
            str(err.value)
            == "Le nouveau point de valorisation doit être un partenaire culturel avec SIRET sur la même entité juridique"
        )
