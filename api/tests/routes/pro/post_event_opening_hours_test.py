import copy
import datetime

import pytest

from pcapi.core.categories import subcategories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.offers.models as offers_models
import pcapi.core.users.factories as users_factories
from pcapi.models import db
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


def _build_opening_hours_dict(partial_dict: dict) -> dict[str, list]:
    opening_hours_dict: dict[str, list] = {}

    for weekday in offers_models.Weekday:
        opening_hours_dict[weekday.name] = []

    opening_hours_dict.update(**partial_dict)
    return opening_hours_dict


@pytest.mark.usefixtures("db_session")
class Returns201Test:
    def test_post_event_opening_hours(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        event_opening_hours_data = copy.deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours", json=event_opening_hours_data
        )

        created_event_opening_hours: offers_models.EventOpeningHours = db.session.query(
            offers_models.EventOpeningHours
        ).one()

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

    def test_post_event_opening_hours_with_no_endDatetime(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        event_opening_hours_data = copy.deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)
        event_opening_hours_data["endDatetime"] = None

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours", json=event_opening_hours_data
        )

        created_event_opening_hours: offers_models.EventOpeningHours = db.session.query(
            offers_models.EventOpeningHours
        ).one()

        assert response.status_code == 201
        assert not response.json["endDatetime"]
        assert not created_event_opening_hours.endDatetime


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
                {"openingHours": _build_opening_hours_dict({"WEDNESDAY": [{"open": "15:00", "close": "14:00"}]})},
                {"openingHours.WEDNESDAY.0.__root__": ["`open` should be before `close`"]},
            ),
            (
                {
                    "openingHours": _build_opening_hours_dict(
                        {"WEDNESDAY": [{"open": "10:00", "close": "14:00"}, {"open": "12:00", "close": "18:00"}]}
                    )
                },
                {"openingHours.WEDNESDAY": ["Time spans overlaps"]},
            ),
            (
                {"openingHours": _build_opening_hours_dict({"WEDNESDAY": [{"open": "24:10", "close": "14:00"}]})},
                {"openingHours.WEDNESDAY.0.open": ["invalid time format"]},
            ),
        ],
    )
    def test_post_event_opening_hours_should_raise_400_because_input_json_invalid(
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

        created_event_opening_hours = db.session.query(offers_models.EventOpeningHours).one_or_none()

        assert response.status_code == 400
        assert response.json == expected_json
        assert not created_event_opening_hours

    def test_post_event_opening_hours_should_raise_because_invalid_category(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.ABO_BIBLIOTHEQUE.id)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours",
            json=_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD,
        )

        created_event_opening_hours = db.session.query(offers_models.EventOpeningHours).one_or_none()

        assert response.status_code == 400
        assert response.json == {"offer.subcategory": ["`ABO_BIBLIOTHEQUE` subcategory does not allow opening hours"]}
        assert not created_event_opening_hours

    def test_post_event_opening_hours_should_raise_because_already_has_opening_hours(self, client):
        offer = offers_factories.EventOpeningHoursFactory().offer
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours",
            json=_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD,
        )

        created_event_opening_hours_count = db.session.query(offers_models.EventOpeningHours).count()

        assert response.status_code == 400
        assert response.json == {"offer": [f"Offer #{offer.id} already has opening hours"]}
        assert created_event_opening_hours_count == 1

    def test_post_event_opening_hours_should_raise_because_already_has_timestamp_stocks(self, client):
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offers_factories.StockFactory(offer=offer)
        offerers_factories.UserOffererFactory(user__email="user@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("user@example.com").post(
            f"/offers/{offer.id}/event_opening_hours",
            json=_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD,
        )

        created_event_opening_hours = db.session.query(offers_models.EventOpeningHours).one_or_none()

        assert response.status_code == 400
        assert response.json == {"offer": [f"Offer #{offer.id} already has timestamped stocks"]}
        assert not created_event_opening_hours


@pytest.mark.usefixtures("db_session")
class Returns403Test:
    def when_user_has_no_rights(self, client, db_session):
        users_factories.ProFactory(email="wrong@example.com")
        offer = offers_factories.EventOfferFactory(subcategoryId=subcategories.FESTIVAL_SPECTACLE.id)
        offerers_factories.UserOffererFactory(user__email="right@example.com", offerer=offer.venue.managingOfferer)

        response = client.with_session_auth("wrong@example.com").post(
            f"/offers/{offer.id}/event_opening_hours",
            json=_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD,
        )

        created_event_opening_hours = db.session.query(offers_models.EventOpeningHours).one_or_none()

        assert response.status_code == 403
        assert response.json == {
            "global": ["Vous n'avez pas les droits d'accès suffisants pour accéder à cette information."]
        }
        assert not created_event_opening_hours
