import pytest
import sqlalchemy as sa

import pcapi.utils.postal_code as postal_code_utils
from pcapi.models import db


def test_get_departement_code_for_mainland_france():
    postal_code = postal_code_utils.PostalCode(postalCode="75012")
    assert postal_code.get_departement_code() == "75"


def test_get_departement_code_for_overseas_france():
    la_reunion_postal_code = postal_code_utils.PostalCode(postalCode="97440")
    assert la_reunion_postal_code.get_departement_code() == "974"

    polynesie_francaise_postal_code = postal_code_utils.PostalCode(postalCode="98700")
    assert polynesie_francaise_postal_code.get_departement_code() == "987"

    guadeloupe_postal_code = postal_code_utils.PostalCode(postalCode="97100")
    assert guadeloupe_postal_code.get_departement_code() == "971"


def test_get_departement_code_for_saint_martin():
    saint_martin_postal_code = postal_code_utils.PostalCode(postalCode="97150")
    assert saint_martin_postal_code.get_departement_code() == "978"


@pytest.mark.parametrize(
    "postal_code, department_code, department_name",
    [
        ("20000", "2A", "Corse-du-Sud"),
        ("20100", "2A", "Corse-du-Sud"),
        ("20200", "2B", "Haute-Corse"),
        ("20600", "2B", "Haute-Corse"),
    ],
)
def test_corsica(postal_code, department_code, department_name):
    postal_code_object = postal_code_utils.PostalCode(postalCode=postal_code)
    assert postal_code_object.get_departement_code() == department_code
    assert postal_code_object.get_departement_name() == department_name

    assert db.session.scalar(sa.func.postal_code_to_department_code(postal_code)) == department_code
