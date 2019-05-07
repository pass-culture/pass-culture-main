import pytest

from domain.departments import get_departement_codes_from_user
from tests.test_utils import create_user


@pytest.mark.standalone
class GetDepartementCodesFromUser:
    def test_returns_offer_in_all_ile_de_france_for_user_from_93(self):
        # given
        user = create_user(departement_code='93')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'75', '77', '78', '91', '92', '93', '94', '95'}

    def test_returns_offer_in_22_25_29_56_for_user_from_29(self):
        # given
        user = create_user(departement_code='29')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'22', '25', '29', '56'}

    def test_returns_offer_in_54_55_57_67_68_88_for_user_from_67(self):
        # given
        user = create_user(departement_code='67')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'54', '55', '57', '67', '68', '88'}

    def test_returns_offer_in_11_12_30_34_48_81_for_user_from_34(self):
        # given
        user = create_user(departement_code='34')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'11', '12', '30', '34', '48', '81'}

    def test_returns_offer_in_97_971_972_973_for_user_from_97(self):
        # given
        user = create_user(departement_code='97')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'97', '971', '972', '973'}

    def test_returns_offer_in_97_971_972_973_for_user_from_973(self):
        # given
        user = create_user(departement_code='973')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'97', '971', '972', '973'}

    def test_returns_offers_only_from_user_departement_for_user_from_remaining_departements(self):
        # given
        user = create_user(departement_code='01')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert departement_codes == ['01']
