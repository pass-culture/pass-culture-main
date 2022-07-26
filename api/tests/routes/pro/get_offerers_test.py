import pytest

from pcapi.core import testing
from pcapi.core.educational.factories import CollectiveOfferFactory
from pcapi.core.educational.factories import CollectiveOfferTemplateFactory
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


def test_access_by_pro(client):
    offerer1 = offerers_factories.OffererFactory(name="offreur B")
    offerer2 = offerers_factories.OffererFactory(name="offreur A")
    offerer3 = offerers_factories.OffererFactory(name="offreur C")
    inactive = offerers_factories.OffererFactory(name="inactive, ignored", isActive=False)
    venue1 = offerers_factories.VenueFactory(managingOfferer=offerer2, name="lieu A1")
    offers_factories.OfferFactory.create_batch(1, venue=venue1)
    venue2 = offerers_factories.VenueFactory(managingOfferer=offerer2, name="lieu A2")
    offers_factories.OfferFactory.create_batch(2, venue=venue2)
    CollectiveOfferFactory(venue=venue2)
    CollectiveOfferTemplateFactory(venue=venue2)

    offerers_factories.VenueFactory(managingOfferer=offerer1, name="lieu B1")
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(offerer=offerer1, user=pro)
    offerers_factories.UserOffererFactory(offerer=offerer2, user=pro)
    offerers_factories.UserOffererFactory(offerer=inactive, user=pro)
    # Non-validated offerers should not be included.
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer3, validationToken="TOKEN")
    # Offerer that belongs to another user should not be returned.
    offerers_factories.OffererFactory(name="not returned")

    client = client.with_session_auth(pro.email)
    n_queries = testing.AUTHENTICATION_QUERIES
    n_queries += 1  # select offerers
    n_queries += 1  # select count of offerers
    n_queries += 1  # select count of offers for all venues
    n_queries += 1  # select count of collective offers for all venues
    n_queries += 1  # select count of collective offers templates for all venues
    with testing.assert_num_queries(n_queries):
        response = client.get("/offerers")

    assert response.status_code == 200
    assert response.json["nbTotalResults"] == 2
    offerers = response.json["offerers"]
    assert len(offerers) == 2
    names = [o["name"] for o in offerers]
    assert names == ["offreur A", "offreur B"]
    venue_ids = {v["id"] for v in offerers[0]["managedVenues"]}
    assert venue_ids == {humanize(venue1.id), humanize(venue2.id)}
    assert offerers[0]["userHasAccess"]
    assert offerers[1]["userHasAccess"]
    assert offerers[0]["nOffers"] == 5
    assert offerers[1]["nOffers"] == 0


def test_access_by_admin(client):
    offerer_b = offerers_factories.OffererFactory(name="offreur B")
    offerers_factories.VenueFactory(managingOfferer=offerer_b)
    offerer_a = offerers_factories.OffererFactory(name="offreur A")
    offerers_factories.VenueFactory(managingOfferer=offerer_a)
    offerers_factories.VenueFactory(managingOfferer=offerer_a)
    offerers_factories.VenueFactory(managingOfferer=offerer_a)
    offerers_factories.UserOffererFactory(offerer=offerer_a)
    offerers_factories.UserOffererFactory(offerer=offerer_a)
    offerers_factories.UserOffererFactory(offerer=offerer_a)
    offerer_c = offerers_factories.OffererFactory(name="offreur C")
    offerers_factories.VenueFactory(managingOfferer=offerer_c)
    admin = users_factories.AdminFactory()

    # Show 2 offerers only (which is less than the number of venues
    # for the first matching offerer). It's intended to problematic
    # `distinct` clause.
    url = "/offerers?keywords=offreur&paginate=2"
    response = client.with_session_auth(admin.email).get(url)

    assert response.status_code == 200
    offerers = response.json["offerers"]
    assert len(offerers) == 2
    assert [o["name"] for o in offerers] == ["offreur A", "offreur B"]
    assert all(o["userHasAccess"] for o in offerers)
    assert response.json["nbTotalResults"] == 3

    response = client.with_session_auth(admin.email).get(url + "&page=2")
    assert response.status_code == 200
    offerers = response.json["offerers"]
    assert len(offerers) == 1
    assert offerers[0]["name"] == "offreur C"
    assert response.json["nbTotalResults"] == 3


def test_filter_on_keywords(client):
    offerer1 = offerers_factories.OffererFactory(name="Cinema")
    offerer2 = offerers_factories.OffererFactory(name="Encore Un Cinema")
    offerer3 = offerers_factories.OffererFactory(name="not matching")
    pro = users_factories.ProFactory()
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)
    offerers_factories.UserOffererFactory(user=pro, offerer=offerer3)

    response = client.with_session_auth(pro.email).get("/offerers?keywords=cinéma")

    assert response.status_code == 200
    offerers = response.json["offerers"]
    assert len(offerers) == 2
    names = [o["name"] for o in offerers]
    assert names == ["Cinema", "Encore Un Cinema"]
