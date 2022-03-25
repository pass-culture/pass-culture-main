import pytest

from pcapi.core import testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_access_by_pro(client):
    offerer1 = offers_factories.OffererFactory(name="offreur B")
    offerer2 = offers_factories.OffererFactory(name="offreur A")
    offerer3 = offers_factories.OffererFactory(name="offreur C")
    inactive = offers_factories.OffererFactory(name="inactive, ignored", isActive=False)
    venue1 = offers_factories.VenueFactory(managingOfferer=offerer2, name="lieu A1")
    offers_factories.OfferFactory.create_batch(1, venue=venue1)
    venue2 = offers_factories.VenueFactory(managingOfferer=offerer2, name="lieu A2")
    offers_factories.OfferFactory.create_batch(2, venue=venue2)
    offers_factories.VenueFactory(managingOfferer=offerer1, name="lieu B1")
    pro = users_factories.ProFactory(offerers=[offerer1, offerer2, inactive])
    # Non-validated offerers should be included, too.
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer3, validationToken="TOKEN")
    # Offerer that belongs to another user should not be returned.
    offers_factories.OffererFactory(name="not returned")

    client = client.with_session_auth(pro.email)
    n_queries = testing.AUTHENTICATION_QUERIES
    n_queries += 1  # select offerers
    n_queries += 1  # select count of offerers
    n_queries += 1  # select count of offers for all venues
    with testing.assert_num_queries(n_queries):
        response = client.get("/offerers")

    assert response.status_code == 200
    assert response.json["nbTotalResults"] == 3
    offerers = response.json["offerers"]
    assert len(offerers) == 3
    names = [o["name"] for o in offerers]
    assert names == ["offreur A", "offreur B", "offreur C"]
    venue_ids = {v["id"] for v in offerers[0]["managedVenues"]}
    assert venue_ids == {humanize(venue1.id), humanize(venue2.id)}
    assert offerers[0]["userHasAccess"]
    assert offerers[1]["userHasAccess"]
    assert not offerers[2]["userHasAccess"]
    assert offerers[0]["nOffers"] == 3
    assert offerers[1]["nOffers"] == 0
    assert offerers[2]["nOffers"] == 0


def test_access_by_admin(client):
    offers_factories.OffererFactory(name="offreur B")
    offers_factories.OffererFactory(name="offreur A")
    offers_factories.OffererFactory(name="offreur C")
    admin = users_factories.AdminFactory()

    response = client.with_session_auth(admin.email).get("/offerers")

    assert response.status_code == 200
    offerers = response.json["offerers"]
    assert len(offerers) == 3
    assert all(o["userHasAccess"] for o in offerers)


def test_filter_on_keywords(client):
    offerer1 = offers_factories.OffererFactory(name="Cinema")
    offerer2 = offers_factories.OffererFactory(name="Encore Un Cinema")
    offerer3 = offers_factories.OffererFactory(name="not matching")
    pro = users_factories.ProFactory(offerers=[offerer1, offerer2, offerer3])
    # Because of a bug, we need venues, here: see bug explained in
    # `get_all_offerers_for_user()`.
    for offerer in (offerer1, offerer2, offerer3):
        offers_factories.VenueFactory(managingOfferer=offerer)

    response = client.with_session_auth(pro.email).get("/offerers?keywords=cinéma")

    assert response.status_code == 200
    offerers = response.json["offerers"]
    assert len(offerers) == 2
    names = [o["name"] for o in offerers]
    assert names == ["Cinema", "Encore Un Cinema"]
