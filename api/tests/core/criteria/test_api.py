import pytest

from pcapi.core.criteria import api
from pcapi.core.criteria import factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


def test_offers_update():
    """
    Test that a bulk criteria update creates the expected OfferCriterion
    objects.
    """
    crit1 = factories.CriterionFactory(name="crit1")
    crit2 = factories.CriterionFactory(name="crit2")
    crit3 = factories.CriterionFactory(name="crit3")

    offer1 = offers_factories.OfferFactory(criteria=[crit1, crit2, crit3])
    offer2 = offers_factories.OfferFactory(criteria=[crit2, crit3])
    offer3 = offers_factories.OfferFactory(criteria=[crit3])

    new_crit1 = factories.CriterionFactory(name="new1")
    new_crit2 = factories.CriterionFactory(name="new2")

    all_criteria = {crit1, crit2, crit3, new_crit1, new_crit2}
    all_criteria_ids = {c.id for c in all_criteria}
    all_offer_ids = [offer1.id, offer2.id, offer3.id]

    api.OfferUpdate(base_ids=all_offer_ids, criteria_ids=all_criteria_ids).run()
    db.session.commit()

    offer1 = offers_models.Offer.query.get(offer1.id)
    offer2 = offers_models.Offer.query.get(offer2.id)
    offer3 = offers_models.Offer.query.get(offer3.id)

    assert set(offer1.criteria) == all_criteria
    assert set(offer2.criteria) == all_criteria
    assert set(offer3.criteria) == all_criteria


def test_venues_update():
    """
    Test that a bulk criteria update creates the expected VenueCriterion
    objects.
    """
    crit1 = factories.CriterionFactory(name="crit1")
    crit2 = factories.CriterionFactory(name="crit2")
    crit3 = factories.CriterionFactory(name="crit3")

    venue1 = offers_factories.VenueFactory(criteria=[crit1, crit2, crit3])
    venue2 = offers_factories.VenueFactory(criteria=[crit2, crit3])
    venue3 = offers_factories.VenueFactory(criteria=[crit3])

    new_crit1 = factories.CriterionFactory(name="new1")
    new_crit2 = factories.CriterionFactory(name="new2")

    all_criteria = {crit1, crit2, crit3, new_crit1, new_crit2}
    all_criteria_ids = {c.id for c in all_criteria}
    all_venue_ids = [venue1.id, venue2.id, venue3.id]

    api.VenueUpdate(base_ids=all_venue_ids, criteria_ids=all_criteria_ids).run()
    db.session.commit()

    venue1 = offerers_models.Venue.query.get(venue1.id)
    venue2 = offerers_models.Venue.query.get(venue2.id)
    venue3 = offerers_models.Venue.query.get(venue3.id)

    assert set(venue1.criteria) == all_criteria
    assert set(venue2.criteria) == all_criteria
    assert set(venue3.criteria) == all_criteria


def test_offers_update_and_replace():
    """
    Test that a bulk update with the replace_tags option does only keep
    the specified criteria.
    """
    crit1 = factories.CriterionFactory(name="crit1")
    crit2 = factories.CriterionFactory(name="crit2")

    offer1 = offers_factories.OfferFactory(criteria=[crit1, crit2])
    offer2 = offers_factories.OfferFactory(criteria=[crit1])
    offer3 = offers_factories.OfferFactory(criteria=[crit2])

    new_crit = factories.CriterionFactory(name="new_crit")

    criteria_ids = [crit1.id, new_crit.id]
    offer_ids = [offer1.id, offer2.id, offer3.id]
    api.OfferUpdate(base_ids=offer_ids, criteria_ids=criteria_ids, replace_tags=True).run()
    db.session.commit()

    offer1 = offers_models.Offer.query.get(offer1.id)
    offer2 = offers_models.Offer.query.get(offer2.id)
    offer3 = offers_models.Offer.query.get(offer3.id)

    expected_criteria = {crit1, new_crit}
    assert set(offer1.criteria) == expected_criteria
    assert set(offer2.criteria) == expected_criteria
    assert set(offer3.criteria) == expected_criteria
