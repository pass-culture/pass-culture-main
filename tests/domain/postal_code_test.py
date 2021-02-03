from pcapi.domain.postal_code.postal_code import PostalCode


class PostalCodeTest:
    def test_get_departement_code_for_mainland_France(self):
        # given
        postal_code = PostalCode(postalCode="75012")

        # when
        departement_code = postal_code.get_departement_code()

        # then
        assert departement_code == "75"

    def test_get_departement_code_for_overseas_France(self):
        # given
        la_reunion_postal_code = PostalCode(postalCode="97440")
        polynesie_francaise_postal_code = PostalCode(postalCode="98700")

        # when
        la_reunion_departement_code = la_reunion_postal_code.get_departement_code()
        polynesie_francaise__departement_code = polynesie_francaise_postal_code.get_departement_code()

        # then
        assert la_reunion_departement_code == "974"
        assert polynesie_francaise__departement_code == "987"
