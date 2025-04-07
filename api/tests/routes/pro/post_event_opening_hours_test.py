import copy
import datetime

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
from pcapi.utils.date import format_into_utc_date


_base_start_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=4)
_base_end_datetime = _base_start_datetime + datetime.timedelta(days=4)

_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD = {
    "startDatetime": format_into_utc_date(_base_start_datetime),
    "endDatetime": format_into_utc_date(_base_end_datetime),
    "openingHours": {
        "MONDAY": [],
        "TUESDAY": [],
        "WEDNESDAY": [{"open": "10:00", "close": "14:00"}],
        "THURSDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "18:00"}],
        "FRIDAY": [],
        "SATURDAY": [],
        "SUNDAY": [],
    },
}


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_create_event_opening_hours(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        event_opening_hours_data = copy.deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours", json=event_opening_hours_data
        )

        created_event_opening_hours: offers_models.EventOpeningHours = offers_models.EventOpeningHours.query.one()

        assert response.status_code == 201
        assert response.json["id"] == created_event_opening_hours.id
        assert response.json["openingHours"] == {
            "MONDAY": [],
            "TUESDAY": [],
            "WEDNESDAY": [{"open": "10:00", "close": "14:00"}],
            "THURSDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "18:00"}],
            "FRIDAY": [],
            "SATURDAY": [],
            "SUNDAY": [],
        }
        assert response.json["startDatetime"] == format_into_utc_date(_base_start_datetime)
        assert response.json["endDatetime"] == format_into_utc_date(_base_end_datetime)

        assert set(
            weekDayOpeningHours.weekday for weekDayOpeningHours in created_event_opening_hours.weekDayOpeningHours
        ) == set([offers_models.Weekday.WEDNESDAY, offers_models.Weekday.THURSDAY])


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @pytest.mark.parametrize(
        "partial_input_json,expected_json",
        [
            (
                {
                    "startDatetime": format_into_utc_date(_base_start_datetime),
                    "endDatetime": format_into_utc_date(_base_start_datetime - datetime.timedelta(days=1)),
                },
                {"__root__": ["`endDatetime` must be superior to `startDatetime`"]},
            ),
            (
                {"endDatetime": format_into_utc_date(_base_start_datetime + datetime.timedelta(days=371))},
                {"__root__": ["Your event cannot last for more than a year"]},
            ),
            (
                {
                    "startDatetime": format_into_utc_date(_base_start_datetime + datetime.timedelta(days=401)),
                    "endDatetime": format_into_utc_date(_base_start_datetime + datetime.timedelta(days=750)),
                },
                {"__root__": ["Your event cannot end in more than two years from now"]},
            ),
            (
                {
                    "openingHours": {
                        "MONDAY": [],
                        "TUESDAY": [],
                        "WEDNESDAY": [{"open": "15:00", "close": "14:00"}],
                        "THURSDAY": [{"open": "10:00", "close": "14:00"}, {"open": "16:00", "close": "18:00"}],
                        "FRIDAY": [],
                        "SATURDAY": [],
                        "SUNDAY": [],
                    }
                },
                {"openingHours.WEDNESDAY.0.__root__": ["`open` should be before `close`"]},
            ),
        ],
    )
    def test_create_event_opening_hours_should_raise_400_because_input_json_invalid(
        self, client, partial_input_json, expected_json
    ):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        event_opening_hours_data = copy.deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)
        event_opening_hours_data.update(**partial_input_json)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours",
            json=event_opening_hours_data,
        )

        created_event_opening_hours = offers_models.EventOpeningHours.query.one_or_none()

        assert response.status_code == 400
        assert response.json == expected_json
        assert not created_event_opening_hours
