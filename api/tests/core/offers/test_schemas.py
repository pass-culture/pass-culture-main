from datetime import time

import pytest

import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.exceptions as offers_exceptions
from pcapi.core.categories import subcategories
from pcapi.core.offers import schemas


pytestmark = pytest.mark.usefixtures("db_session")


class PostDraftOfferBodyModelTest:
    def test_post_draft_offer_body_model(self):
        venue = offerers_factories.VirtualVenueFactory()
        _ = schemas.PostDraftOfferBodyModel(
            name="Name",
            subcategoryId=subcategories.ABO_PLATEFORME_VIDEO.id,
            venueId=venue.id,
            description="description",
            durationMinutes=12,
            extraData={"ean": "12345678910111"},
        )


class PatchDraftOfferBodyModelTest:
    def test_patch_draft_offer_body_model(self):
        _ = schemas.PatchDraftOfferBodyModel(
            name="Name", description="description", extraData={"artist": "An-2"}, durationMinutes=12
        )

    def test_patch_offer_with_invalid_subcategory(self):
        with pytest.raises(offers_exceptions.OfferException) as error:
            _ = schemas.PatchDraftOfferBodyModel(
                name="I solemnly swear that my intentions are evil",
                subcategoryId="Misconduct fullfield",
            )

        assert error.value.errors["subcategory"] == ["La sous-catégorie de cette offre est inconnue"]


class OfferOpeningHoursSchemaTest:
    def test_empty_opening_hours_is_valid(self):
        oh = schemas.OfferOpeningHoursSchema(openingHours={})
        assert oh.openingHours == {}

    def test_many_days_with_some_timespans_or_not_is_ok(self):
        oh = schemas.OfferOpeningHoursSchema(
            openingHours={
                "MONDAY": [["10:00", "13:00"], ["14:00", "17:00"]],
                "FRIDAY": [["12:00", "19:00"]],
                "SUNDAY": None,
            }
        )

        assert oh.openingHours["MONDAY"] == [["10:00", "13:00"], ["14:00", "17:00"]]
        assert oh.openingHours["FRIDAY"] == [["12:00", "19:00"]]

    def test_none_opening_hours_is_not_ok(self):
        with pytest.raises(ValueError, match="none is not an allowed value"):
            schemas.OfferOpeningHoursSchema(openingHours=None)

    @pytest.mark.parametrize(
        "timespans",
        [
            [["10:00", "13:00", "19:00"]],  # too many items
            [["10:00"]],  # not enough items
            [[]],  # not enough items
            [],  # not enough items
        ],
    )
    def test_invalid_opening_hour_timespans_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="ensure this value has at"):  # has at least/most
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": timespans})

    @pytest.mark.parametrize(
        "timespans",
        [
            [["1:", "10:00"]],  # should be 01:00 (minutes missing)
            [["1:00", "10:00"]],  # should be 01:00
            [["29:00", "10:00"]],  # hour error
            [["24:00", "10:00"]],  # hour error (should be 00:00)
            [["12:99", "10:00"]],  # minutes error
            [["1200", "10:00"]],  # missing time separator
            [["12T01", "10:00"]],  # unexpected time separator
            [["12 02", "10:00"]],  # another unexpected time separator
            [["10:00:00:00:00", "18:00"]],  # not a valid iso time
        ],
    )
    def test_malformed_timespan_is_not_a_valid_hour_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="string does not match regex"):
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": timespans})

    @pytest.mark.parametrize(
        "timespans",
        [
            [[time(10), "18:00"]],  # time objects are not valid (only str)
            [[10 * 60, "18:00"]],  # int is not a valid data type
        ],
    )
    def test_invalid_timespan_data_type_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="str type expected"):
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": timespans})

    def test_null_timespan_is_not_ok(self):
        with pytest.raises(ValueError, match="none is not an allowed value"):
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": [[None, "18:00"]]})

    @pytest.mark.parametrize(
        "timespans",
        [
            [["10:00", "18:00"], ["12:00", "15:00"]],  # overlap: inside
            [["10:00", "16:00"], ["12:00", "19:00"]],  # overlap: inside/outside
        ],
    )
    def test_overlapping_timespans_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="overlapping"):
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": timespans})

    @pytest.mark.parametrize("weekday", ["MNDAY", "monday", "OOPS", 1])
    def test_unknown_weekday_is_not_valid(self, weekday):
        with pytest.raises(ValueError, match="value is not a valid enumeration member"):
            schemas.OfferOpeningHoursSchema(openingHours={weekday: [["10:00", "18:00"]]})

    def test_none_is_not_a_valid_weekday(self):
        with pytest.raises(ValueError, match="none is not an allowed value"):
            schemas.OfferOpeningHoursSchema(openingHours={None: [["10:00", "18:00"]]})
