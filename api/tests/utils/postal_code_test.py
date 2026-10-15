import pytest
import sqlalchemy as sa

import pcapi.utils.postal_code as postal_code_utils
from pcapi.models import db


@pytest.mark.parametrize(
    "postal_code, department_code, department_name",
    [
        ("20000", "2A", "Corse-du-Sud"),
        ("20100", "2A", "Corse-du-Sud"),
        ("20200", "2B", "Haute-Corse"),
        ("20600", "2B", "Haute-Corse"),
        ("75012", "75", "Paris"),
        ("97055", "978", "Saint-Martin"),  # Cedex
        ("97079", "978", "Saint-Martin"),  # Cedex
        ("97095", "977", "Saint-Barthélemy"),  # Cedex
        ("97133", "977", "Saint-Barthélemy"),
        ("97150", "978", "Saint-Martin"),
        ("97440", "974", "La Réunion"),
        ("97100", "971", "Guadeloupe"),
        ("98700", "987", "Polynésie française"),
    ],
)
def test_get_departement_code(postal_code, department_code, department_name):
    postal_code_object = postal_code_utils.PostalCode(postalCode=postal_code)
    assert postal_code_object.get_departement_code() == department_code
    assert postal_code_object.get_departement_name() == department_name

    assert db.session.scalar(sa.func.postal_code_to_department_code(postal_code)) == department_code
