import datetime
from copy import deepcopy

import pytest
import pytz

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.offers.schemas import CreateEventOpeningHoursModel
from pcapi.core.offers.schemas import PatchDraftOfferBodyModel
from pcapi.core.offers.schemas import PostDraftOfferBodyModel


pytestmark = pytest.mark.usefixtures("db_session")


class PostDraftOfferBodyModelTest:
    def test_post_draft_offer_body_model(self):
        venue = offerers_factories.VirtualVenueFactory()
        _ = PostDraftOfferBodyModel(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venueId=venue.id,
            description="description",
            durationMinutes=12,
            extraData={"ean": "12345678910111"},
        )


_base_start_datetime = datetime.datetime.utcnow() + datetime.timedelta(days=4)
_base_end_datetime = _base_start_datetime + datetime.timedelta(days=4)

_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD = {
    "startDatetime": _base_start_datetime.astimezone(pytz.utc),
    "endDatetime": _base_end_datetime.astimezone(pytz.utc),
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


class CreateEventOpeningHoursModelTest:
    def test_create_event_opening_hours_model(self):
        _ = CreateEventOpeningHoursModel(**_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)

    @pytest.mark.parametrize(
        "input_dict,expected_error",
        [
            (
                {"endDatetime": (_base_start_datetime - datetime.timedelta(days=1)).astimezone(pytz.utc)},
                "`endDatetime` must be superior to `startDatetime`",
            ),
            (
                {"endDatetime": (_base_start_datetime + datetime.timedelta(days=380)).astimezone(pytz.utc)},
                "Your event cannot last for more than a year",
            ),
            (
                {
                    "startDatetime": (datetime.datetime.utcnow() + datetime.timedelta(days=400)).astimezone(pytz.utc),
                    "endDatetime": (datetime.datetime.utcnow() + datetime.timedelta(days=751)).astimezone(pytz.utc),
                },
                "Your event cannot end in more than two years from now",
            ),
        ],
    )
    def test_create_event_opening_hours_model_should_raise_datetime_errors(self, input_dict, expected_error):
        json_dict = deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)
        json_dict.update(**input_dict)

        with pytest.raises(ValueError) as error:
            _ = CreateEventOpeningHoursModel(**json_dict)

        assert expected_error in str(error.value.errors)

    @pytest.mark.parametrize(
        "input_dict,expected_error",
        [
            ({"WEDNESDAY": [{"open": "15:00", "close": "14:00"}]}, "`open` should be before `close`"),
            (
                {"WEDNESDAY": [{"open": "14:00", "close": "16:00"}, {"open": "15:00", "close": "17:00"}]},
                "Time spans overlaps",
            ),
            (
                {"WEDNESDAY": [{"open": "14:00", "close": "16:00"}, {"open": "15:00", "close": "15:30"}]},
                "Time spans overlaps",
            ),
            (
                {
                    "WEDNESDAY": [
                        {"open": "14:00", "close": "16:00"},
                        {"open": "16:50", "close": "17:00"},
                        {"open": "17:50", "close": "18:00"},
                    ]
                },
                "ensure this value has at most 2 items",
            ),
        ],
    )
    def test_create_event_opening_hours_model_should_raise_opening_hours_errors(self, input_dict, expected_error):
        json_dict = deepcopy(_FUNCTIONAL_CREATE_EVENT_OPENING_HOURS_PAYLOAD)
        json_dict["openingHours"].update(**input_dict)

        with pytest.raises(ValueError) as error:
            _ = CreateEventOpeningHoursModel(**json_dict)

        assert expected_error in str(error.value.errors)


class PatchDraftOfferBodyModelTest:
    def test_patch_draft_offer_body_model(self):
        _ = PatchDraftOfferBodyModel(
            name="Name", description="description", extraData={"artist": "An-2"}, durationMinutes=12
        )

    def test_patch_offer_with_invalid_subcategory(self):
        with pytest.raises(offers_exceptions.UnknownOfferSubCategory) as error:
            _ = PatchDraftOfferBodyModel(
                name="I solemnly swear that my intentions are evil",
                subcategoryId="Misconduct fullfield",
            )

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]
