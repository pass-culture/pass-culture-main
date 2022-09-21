import pcapi.utils.postal_code as postal_code_utils


def test_get_departement_code_for_mainland_france():
    postal_code = postal_code_utils.PostalCode(postalCode="75012")
    assert postal_code.get_departement_code() == "75"


def test_get_departement_code_for_overseas_france():
    la_reunion_postal_code = postal_code_utils.PostalCode(postalCode="97440")
    assert la_reunion_postal_code.get_departement_code() == "974"

    polynesie_francaise_postal_code = postal_code_utils.PostalCode(postalCode="98700")
    assert polynesie_francaise_postal_code.get_departement_code() == "987"
