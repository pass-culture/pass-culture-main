import decimal

import pytest

from pcapi.connectors.api_adresse import format_payload
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.core.testing import override_settings
from pcapi.scripts.venue.fix_ban_ids import main

from tests.connectors.api_adresse import fixtures


@pytest.mark.usefixtures("db_session")
class FixBanIdsTest:
    @override_settings(ADRESSE_BACKEND="pcapi.connectors.api_adresse.ApiAdresseBackend")
    def test_script(self, requests_mock, client, db_session):
        text = format_payload(fixtures.SEARCH_CSV_HEADERS, fixtures.SEARCH_CSV_RESULTS)
        requests_mock.post("https://api-adresse.data.gouv.fr/search/csv", text=text)

        venue_type_code = offerers_models.VenueTypeCode.LIBRARY  # Permanent

        # Matching ban_id:
        offerers_factories.VenueFactory(
            id=1,
            banId="38185_1660_00033",
            venueTypeCode=venue_type_code,
        )

        # Mismatching ban_id / Wrong ban_id / Housenumber / Fixable:
        offerers_factories.VenueFactory(
            id=2,
            banId="38185_3000_00033",
            venueTypeCode=venue_type_code,
        )

        # Mismatching ban_id / Missing ban_id / Housenumber / Fixable:
        offerers_factories.VenueFactory(
            id=3,
            banId=None,
            venueTypeCode=venue_type_code,
        )

        # Mismatching ban_id / Wrong ban_id / Street / Fixable:
        offerers_factories.VenueFactory(
            id=4,
            banId="38185_3000_00033",
            venueTypeCode=venue_type_code,
        )

        # Mismatching ban_id / Missing ban_id / Street / Non-fixable:
        offerers_factories.VenueFactory(
            id=5,
            banId=None,
            venueTypeCode=venue_type_code,
        )

        # Run fix_ban_ids script:
        main(dry_run=False)

        # Matching ban_id:
        venue = offerers_models.Venue.query.filter_by(1).one()
        assert venue.banId == "38185_1660_00033"
        assert venue.latitude == decimal.Decimal("48.87004")
        assert venue.longitude == decimal.Decimal("2.37850")

        # Mismatching ban_id / Wrong ban_id / Housenumber / Fixable:
        venue = offerers_models.Venue.query.filter_by(2).one()
        assert venue.banId == "38185_1660_00033"
        assert venue.latitude == decimal.Decimal("45.18403")
        assert venue.longitude == decimal.Decimal("5.74029")

        # Mismatching ban_id / Missing ban_id / Housenumber / Fixable:
        venue = offerers_models.Venue.query.filter_by(3).one()
        assert venue.banId == "38185_1660_00033"
        assert venue.latitude == decimal.Decimal("45.18403")
        assert venue.longitude == decimal.Decimal("5.74029")

        # Mismatching ban_id / Wrong ban_id / Street / Fixable:
        venue = offerers_models.Venue.query.filter_by(4).one()
        assert venue.banId == "38185_1660"
        assert venue.latitude == decimal.Decimal("45.18381")
        assert venue.longitude == decimal.Decimal("5.73968")

        # Mismatching ban_id / Missing ban_id / Street / Non-fixable:
        venue = offerers_models.Venue.query.filter_by(5).one()
        assert venue.banId is None
        assert venue.latitude == decimal.Decimal("48.87004")
        assert venue.longitude == decimal.Decimal("2.37850")
