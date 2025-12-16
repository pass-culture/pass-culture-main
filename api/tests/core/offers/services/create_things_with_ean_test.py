from datetime import UTC
from datetime import datetime

import pytest

from pcapi.core.categories import subcategories
from pcapi.core.offerers import schemas as offerers_schemas
from pcapi.core.offers.services import create_things_with_ean as service


def mandatory_data():
    return {
        "name": f"some {subcategories.LIVRE_PAPIER.id} offer",
        "subcategoryId": subcategories.LIVRE_PAPIER.id,
        "venue": {"id": 1, "code": offerers_schemas.VenueTypeCode.BOOKSTORE},
        "audioDisabilityCompliant": False,
        "mentalDisabilityCompliant": False,
        "motorDisabilityCompliant": False,
        "visualDisabilityCompliant": False,
    }


class CreateLivrePapierTest:
    def test_mandatory_data_only_should_be_ok(self):
        service.LivrePapierModel(**mandatory_data())

    def test_unknown_parameter_is_rejected(self):
        inputs = {**mandatory_data(), "unknown": "reject"}
        with pytest.raises(ValueError):
            service.LivrePapierModel(**inputs)

    @pytest.mark.parametrize("wrong_input", [
        "not_a_kwargs", True, pytest.param(datetime.now(UTC), id="utcnow")
    ])
    def test_wrong_input_is_rejected(self, wrong_input):
        with pytest.raises(TypeError):
            service.LivrePapierModel(wrong_input)
