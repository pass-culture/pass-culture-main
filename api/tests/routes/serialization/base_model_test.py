import decimal

from pydantic import ValidationError
import pytest
from pytest import fixture

from pcapi.routes.serialization import BaseModel


class FloatModel(BaseModel):
    float_number: float


class DecimalModel(BaseModel):
    decimal_number: decimal.Decimal


class BaseModelTest:
    @pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
    def test_float_does_not_allow_invalid_numbers(self, value: str, app: fixture):
        with pytest.raises(ValidationError):
            FloatModel(float_number=float(value))

    @pytest.mark.parametrize("value", ["nan", "inf", "-inf"])
    def test_decimal_does_not_allow_invalid_numbers(self, value: str, app: fixture):
        with pytest.raises(ValidationError):
            DecimalModel(decimal_number=value)
