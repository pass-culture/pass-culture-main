import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
from pcapi.scripts.fill_oh_from_wd.main import fill_oh_from_wd


@pytest.mark.usefixtures("db_session")
class FillOpeningHoursFromWithdrawalDetailsTest:
    def test_script(self, db_session):
        venue_type_code = offerers_models.VenueTypeCode.LIBRARY  # Permanent

        # Missing Opening Hours:
        offerers_factories.VenueFactory(
            id=1,
            venueTypeCode=venue_type_code,
            withdrawalDetails="Ouvert du lundi au vendredi de 9h à 12h et de 14h à 18h",
        )
        offerers_models.OpeningHours.query.filter(offerers_models.OpeningHours.venueId == 1).delete()

        # Existing Opening Hours:
        offerers_factories.VenueFactory(
            id=2,
            venueTypeCode=venue_type_code,
            withdrawalDetails="Ouvert du lundi au vendredi de 9h à 12h et de 14h à 18h",
        )

        # Run fill_opening_hours_from_withdrawal_details script:
        fill_oh_from_wd(dry_run=False)

        # Missing Opening Hours:
        venue = offerers_models.Venue.query.get(1)
        assert venue.opening_days == {
            "MONDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "TUESDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "WEDNESDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "THURSDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "FRIDAY": [{"open": "09:00", "close": "12:00"}, {"open": "14:00", "close": "18:00"}],
            "SATURDAY": None,
            "SUNDAY": None,
        }

        # Existing Opening Hours:
        venue = offerers_models.Venue.query.get(2)
        assert venue.opening_days == {
            "MONDAY": [{"open": "14:00", "close": "19:30"}],
            "TUESDAY": [{"open": "10:00", "close": "13:00"}, {"open": "14:00", "close": "19:30"}],
            "WEDNESDAY": [{"open": "10:00", "close": "13:00"}, {"open": "14:00", "close": "19:30"}],
            "THURSDAY": [{"open": "10:00", "close": "13:00"}, {"open": "14:00", "close": "19:30"}],
            "FRIDAY": [{"open": "10:00", "close": "13:00"}, {"open": "14:00", "close": "19:30"}],
            "SATURDAY": [{"open": "10:00", "close": "13:00"}, {"open": "14:00", "close": "19:30"}],
            "SUNDAY": None,
        }
