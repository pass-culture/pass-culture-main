import pytest

from pcapi.core.offers.defs import validate
from pcapi.core.offers.defs.models.things import PartitionModel


class PartialValidationTest:
    def test_valid_inputs_does_not_raise_an_error(self):
        validate.partial_validation(
            PartitionModel,
            name="some offer",
            venue={"id": 1, "code": "BOOKSTORE"},
            audio_disability_compliant=False,
            mental_disability_compliant=False,
            visual_disability_compliant=False,
            motor_disability_compliant=False,
            extra_data={},
        )

    def test_partial_but_valid_inputs_does_not_raises_an_error(self):
        validate.partial_validation(
            PartitionModel,
            name="some offer",
            venue={"id": 1, "code": "BOOKSTORE"},
            audio_disability_compliant=False,
            mental_disability_compliant=False,
            visual_disability_compliant=False,
            motor_disability_compliant=False,
        )

    def test_missing_mandatory_input_raises_an_error(self):
        with pytest.raises(validate.InputValidationError, match="errors: {'venue'}"):
            # missing: venue
            validate.partial_validation(
                PartitionModel,
                name="some offer",
                audio_disability_compliant=False,
                mental_disability_compliant=False,
                visual_disability_compliant=False,
                motor_disability_compliant=False,
                extra_data={},
            )

    def test_unknown_input_raises_an_error(self):
        with pytest.raises(validate.InputValidationError, match="errors: {'extra_data.speaker'}"):
            validate.partial_validation(
                PartitionModel,
                name="some offer",
                venue={"id": 1, "code": "BOOKSTORE"},
                audio_disability_compliant=False,
                mental_disability_compliant=False,
                visual_disability_compliant=False,
                motor_disability_compliant=False,
                extra_data={"speaker": "Unexpected"},
            )

    def test_known_but_malformed_field_raises_an_error(self):
        with pytest.raises(validate.InputValidationError, match="errors: {'extra_data.ean'}"):
            validate.partial_validation(
                PartitionModel,
                name="some offer",
                venue={"id": 1, "code": "BOOKSTORE"},
                audio_disability_compliant=False,
                mental_disability_compliant=False,
                visual_disability_compliant=False,
                motor_disability_compliant=False,
                extra_data={"ean": 123},
            )
