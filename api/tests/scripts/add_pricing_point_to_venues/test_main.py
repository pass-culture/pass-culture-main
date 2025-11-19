import typing

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.scripts.add_pricing_point_to_venues import main


pytestmark = pytest.mark.usefixtures("db_session")


def fake_iterator(venue_id) -> typing.Iterator[dict]:
    yield {"venue_id": str(venue_id)}


def test_add_pp_to_venues(monkeypatch):
    venue_without_pp = offerers_factories.VenueFactory.create(siret=None, comment="comment")
    venue_without_siret = offerers_factories.VenueFactory.create(
        siret=None, comment="comment", managingOfferer=venue_without_pp.managingOfferer
    )
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_without_siret,
        pricingPoint=venue_without_siret,
    )
    venue_with_siret = offerers_factories.VenueFactory.create(managingOfferer=venue_without_pp.managingOfferer)
    offerers_factories.VenuePricingPointLinkFactory.create(
        venue=venue_with_siret,
        pricingPoint=venue_with_siret,
    )

    monkeypatch.setattr(main, "_read_csv_file", lambda: fake_iterator(venue_without_pp.id))

    main.main(not_dry=True)
    assert venue_without_pp.current_pricing_point == venue_with_siret
