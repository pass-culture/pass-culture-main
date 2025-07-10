from datetime import time

import pytest

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import factories
from pcapi.core.offers.opening_hours import api
from pcapi.models import db


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
    expected_timespans example: [[time(10), time(12)], [time(13), time(20)]]
    """
    assert len(fetched_timespans) == len(expected_timespans)

    fetched_timespans = sorted(fetched_timespans, key=lambda ts: ts.lower)
    expected_timespans = sorted(expected_timespans, key=lambda oh: oh[0])

    for fetched, expected in zip(fetched_timespans, expected_timespans):
        assert fetched.lower == expected[0].hour * 60 + expected[0].minute
        assert fetched.upper == expected[1].hour * 60 + expected[1].minute


class CreateOpeningHoursTest:
    def test_create_one_weekday_with_one_timespan(self, offer):
        opening_hours = {offerers_models.Weekday.MONDAY: [[time(10), time(18)]]}
        api.create_opening_hours(offer, opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY

        validate_timespans(oh.timespan, opening_hours[offerers_models.Weekday.MONDAY])

    def test_create_many_weekdays_with_some_timespans(self, offer):
        opening_hours = {
            offerers_models.Weekday.MONDAY: [[time(10), time(18)]],
            offerers_models.Weekday.WEDNESDAY: [[time(11), time(12, 30)], [time(14), time(19)]],
            offerers_models.Weekday.FRIDAY: [[time(12), time(20)]],
        }
        api.create_opening_hours(offer, opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == len(opening_hours)

        weekdays = {oh.weekday for oh in db.session.query(offerers_models.OpeningHours)}
        assert weekdays == opening_hours.keys()

        for weekday, timespans in opening_hours.items():
            oh = db.session.query(offerers_models.OpeningHours).filter_by(weekday=weekday).first()
            validate_timespans(oh.timespan, timespans)

    def test_create_one_weekday_with_opening_hours_erases_all_existing_ones(self, offer):
        # shoudl all be deleted
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.MONDAY)
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.SATURDAY)
        offerers_factories.OpeningHoursFactory(venue=None, offer=offer, weekday=offerers_models.Weekday.SUNDAY)

        opening_hours = {offerers_models.Weekday.MONDAY: [[time(10), time(18)]]}
        api.create_opening_hours(offer, opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY
        validate_timespans(oh.timespan, opening_hours[offerers_models.Weekday.MONDAY])

    def test_create_opening_hours_without_timespans_is_ok_but_creates_nothing(self, offer):
        api.create_opening_hours(offer, {offerers_models.Weekday.TUESDAY: None})
        assert db.session.query(offerers_models.OpeningHours).count() == 0

    def test_create_opening_hours_with_empty_timespans_is_ok_but_creates_nothing(self, offer):
        api.create_opening_hours(offer, {offerers_models.Weekday.TUESDAY: []})
        assert db.session.query(offerers_models.OpeningHours).count() == 0

    def test_create_opening_hours_with_some_missing_timespans_is_ok(self, offer):
        opening_hours = {offerers_models.Weekday.MONDAY: [[time(10), time(18)]], offerers_models.Weekday.THURSDAY: None}
        api.create_opening_hours(offer, opening_hours)

        assert db.session.query(offerers_models.OpeningHours).count() == 1

        oh = db.session.query(offerers_models.OpeningHours).first()
        assert oh.weekday == offerers_models.Weekday.MONDAY

        validate_timespans(oh.timespan, opening_hours[offerers_models.Weekday.MONDAY])

    def test_null_opening_hours_is_valid_but_creates_nothing(self, offer):
        api.create_opening_hours(offer, None)
        assert db.session.query(offerers_models.OpeningHours).count() == 0
