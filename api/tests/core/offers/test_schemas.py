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

        assert oh.openingHours["MONDAY"] == [[time(10), time(13)], [time(14), time(17)]]
        assert oh.openingHours["FRIDAY"] == [[time(12), time(19)]]

    def test_mixing_str_and_time_objects_is_ok(self):
        oh = schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": [["10:00", time(18)]]})
        assert oh.openingHours["MONDAY"] == [[time(10), time(18)]]

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
    def test_timespan_is_not_a_valid_hour_is_not_ok(self, timespans):
        with pytest.raises(ValueError, match="invalid time format"):
            schemas.OfferOpeningHoursSchema(openingHours={"MONDAY": timespans})

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
