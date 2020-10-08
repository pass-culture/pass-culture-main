from pcapi.domain.postal_code.postal_code import PostalCode


class PostalCodeTest:
    def test_get_departement_code_for_mainland_France(self):
        # given
        postal_code = PostalCode(postalCode='75012')

        # when
        departement_code = postal_code.get_departement_code()

        # then
        assert departement_code == '75'

    def test_get_departement_code_for_overseas_France(self):
        # given
        postal_code = PostalCode(postalCode='97440')

        # when
        departement_code = postal_code.get_departement_code()

        # then
        assert departement_code == '974'
