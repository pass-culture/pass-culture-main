import typing

import pytest

from pcapi.core.offers.services import models
from pcapi.core.offers.services import utils


class Legit(models.Base):
    subcategory_id: typing.Literal["LIVRE_PAPIER"]


class Legit(models.Base):
    subcategory_id: typing.Literal["LIVRE_PAPIER"]


class WithUnknown(models.Base):
    subcategory_id: "UNKNOWN"


class WithoutStrLiteral(models.Base):
    subcategory_id: "LIVRE_PAPIER"


class WithoutSubcategoryId(models.Base):
    something: int


class ExtractSubcategoryTest:
    def test_model_with_a_subcategory_as_a_str_literal_works(self):
        assert utils.extract_subcategory(Legit) == "LIVRE_PAPIER"

    def test_model_with_an_unknown_subcategory_fails(self):
        with pytest.raises(IndexError):
            utils.extract_subcategory(WithUnknown)

    def test_model_with_a_subcategory_that_is_not_a_literail_fails(self):
        with pytest.raises(IndexError):
            utils.extract_subcategory(WithoutStrLiteral)

    def test_model_without_subcategory_raises_an_error(self):
        with pytest.raises(KeyError):
            utils.extract_subcategory(WithoutSubcategoryId)
