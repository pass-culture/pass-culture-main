import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.models import db
from pcapi.scripts.correct_venue_collective_phone import main as correction_script


pytestmark = pytest.mark.usefixtures("clean_database")


class IsCountryCodeOnlyTest:
    @pytest.mark.parametrize(
        "raw_phone",
        [
            "+33",
            "33",
            "0033",
            "+590",
            "590",
            "00 590",
            "+262",
            "  + 687  ",
        ],
    )
    def test_returns_true_for_country_code_only_values(self, raw_phone: str) -> None:
        assert correction_script._is_country_code_only(raw_phone)

    @pytest.mark.parametrize(
        "raw_phone",
        [
            "+33612345678",
            "0612345678",
            "+590690001122",
            "",
            "abc",
            "+999",
        ],
    )
    def test_returns_false_for_actual_phone_numbers_or_unknown_codes(self, raw_phone: str) -> None:
        assert not correction_script._is_country_code_only(raw_phone)


class MainTest:
    def test_dry_run_does_not_persist_changes(self) -> None:
        invalid_venue = offerers_factories.VenueFactory(collectivePhone="+33")
        valid_venue = offerers_factories.VenueFactory(collectivePhone="+33612345678")

        correction_script.main(apply=False)

        db.session.expire_all()
        invalid_venue_refreshed = db.session.get(type(invalid_venue), invalid_venue.id)
        valid_venue_refreshed = db.session.get(type(valid_venue), valid_venue.id)

        assert invalid_venue_refreshed is not None
        assert valid_venue_refreshed is not None
        assert invalid_venue_refreshed.collectivePhone == "+33"
        assert valid_venue_refreshed.collectivePhone == "+33612345678"

    def test_apply_persists_changes_for_country_code_only_values(self) -> None:
        invalid_venue = offerers_factories.VenueFactory(collectivePhone="0033")
        valid_venue = offerers_factories.VenueFactory(collectivePhone="+33612345678")

        correction_script.main(apply=True)

        db.session.expire_all()
        invalid_venue_refreshed = db.session.get(type(invalid_venue), invalid_venue.id)
        valid_venue_refreshed = db.session.get(type(valid_venue), valid_venue.id)

        assert invalid_venue_refreshed is not None
        assert valid_venue_refreshed is not None
        assert invalid_venue_refreshed.collectivePhone is None
        assert valid_venue_refreshed.collectivePhone == "+33612345678"
