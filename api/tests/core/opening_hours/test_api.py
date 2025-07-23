import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories
from pcapi.core.opening_hours import api
from pcapi.core.opening_hours import schemas
from pcapi.models import db
from pcapi.utils.date import timespan_str_to_numrange


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(name="venue")
def venue_fixture():
    return offerers_factories.VenueFactory()


@pytest.fixture(name="offer")
def offer_fixture(venue):
    return factories.ThingOfferFactory(venue=venue)


def validate_timespans(fetched_timespans, expected_timespans):
    """Check that timespans fetched from the DB matched the input timespans

    fetched_timespans example: [NumericRange(600, 720), NumericRange(780, 1200)]
    expected_timespans example: [["10:00", "12:00"], ["13:00", "20:00"]]
    """
    fetched_timespans = sorted(fetched_timespans, key=lambda ts: ts.lower)
    expected_timespans = sorted(expected_timespans, key=lambda oh: oh[0])

    assert fetched_timespans == timespan_str_to_numrange(expected_timespans)


class UpsertOpeningHoursTest:
    def test_create_one_weekday_with_one_timespan(self, offer):
        opening_hours = schemas.WeekdayOpeningHoursTimespans(MONDAY=[["10:00", "18:00"]])
        api.upsert_opening_hours(offer, opening_hours=opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY

        validate_timespans(oh.timespan, opening_hours.MONDAY)

    def test_create_many_weekdays_with_some_timespans(self, offer):
        opening_hours = schemas.WeekdayOpeningHoursTimespans(
            MONDAY=[["10:00", "18:00"]],
            WEDNESDAY=[["11:00", "12:30"], ["14:00", "19:00"]],
            FRIDAY=[["12:00", "20:00"]],
        )
        api.upsert_opening_hours(offer, opening_hours=opening_hours)

        filtered_opening_hours = {
            weekday: timespans for weekday, timespans in opening_hours.dict().items() if timespans
        }

        found = db.session.query(offerers_models.OpeningHours).count()
        expected = len(list(filtered_opening_hours.values()))
        assert found == expected

        weekdays = {oh.weekday.value for oh in db.session.query(offerers_models.OpeningHours)}
        assert weekdays == set(filtered_opening_hours.keys())

        for raw_weekday, timespans in filtered_opening_hours.items():
            weekday = offerers_models.Weekday[raw_weekday]
            oh = db.session.query(offerers_models.OpeningHours).filter_by(weekday=weekday).first()
            validate_timespans(oh.timespan, timespans)

    def test_create_one_weekday_with_opening_hours_erases_all_existing_ones(self, offer):
        # should all be deleted
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.MONDAY)
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.SATURDAY)
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.SUNDAY)

        opening_hours = schemas.WeekdayOpeningHoursTimespans(MONDAY=[["10:00", "18:00"]])
        api.upsert_opening_hours(offer, opening_hours=opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY
        validate_timespans(oh.timespan, opening_hours.MONDAY)

    def test_upsert_opening_hours_without_timespans_is_ok_but_creates_nothing(self, offer):
        api.upsert_opening_hours(offer, opening_hours=schemas.WeekdayOpeningHoursTimespans(TUESDAY=None))
        assert db.session.query(offerers_models.OpeningHours).count() == 0

    def test_upsert_opening_hours_with_some_missing_timespans_is_ok(self, offer):
        opening_hours = schemas.WeekdayOpeningHoursTimespans(MONDAY=[["10:00", "18:00"]], THURSDAY=None)
        api.upsert_opening_hours(offer, opening_hours=opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY

        validate_timespans(oh.timespan, opening_hours.MONDAY)

    def test_null_opening_hours_is_valid_but_creates_nothing(self, offer):
        api.upsert_opening_hours(offer, opening_hours=None)
        assert db.session.query(offerers_models.OpeningHours).count() == 0
