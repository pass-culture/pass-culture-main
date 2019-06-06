from domain.departments import get_departement_codes_from_user
from tests.test_utils import create_user


class GetDepartementCodesFromUser:
    def test_returns_offer_in_02_08_51_55_59_for_user_from_08(self):
        # given
        user = create_user(departement_code='08')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'02', '08', '51', '55', '59'}

    def test_returns_offer_in_21_25_39_67_68_70_71_90_for_user_from_25(self):
        # given
        user = create_user(departement_code='25')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'21', '25', '39', '67', '68', '70', '71', '90'}

    def test_returns_offer_in_22_35_29_56_for_user_from_29(self):
        # given
        user = create_user(departement_code='29')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'22', '35', '29', '56'}

    def test_returns_offer_in_11_12_13_30_31_34_48_66_81_84_for_user_from_34(self):
        # given
        user = create_user(departement_code='34')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'11', '12', '13', '30', '31', '34', '48', '66', '81', '84'}

    def test_returns_offer_in_22_29_35_44_49_50_53_56_for_user_from_35(self):
        # given
        user = create_user(departement_code='35')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'22', '29', '35', '44', '49', '50', '53', '56'}

    def test_returns_offer_in_03_18_21_45_58_71_89_for_user_from_58(self):
        # given
        user = create_user(departement_code='58')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'03', '18', '21', '45', '58', '71', '89'}

    def test_returns_offer_in_54_55_57_67_68_88_for_user_from_67(self):
        # given
        user = create_user(departement_code='67')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'54', '55', '57', '67', '68', '88'}

    def test_returns_offer_in_01_03_21_39_42_58_69_71_for_user_from_71(self):
        # given
        user = create_user(departement_code='71')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'01', '03', '21', '39', '42', '58', '69', '71'}

    def test_returns_offer_in_04_07_13_26_30_83_84_for_user_from_84(self):
        # given
        user = create_user(departement_code='84')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'04', '07', '13', '26', '30', '83', '84'}

    def test_returns_offer_in_all_ile_de_france_for_user_from_93(self):
        # given
        user = create_user(departement_code='93')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'75', '77', '78', '91', '92', '93', '94', '95'}

    def test_returns_offer_in_all_ile_de_france_for_user_from_94(self):
        # given
        user = create_user(departement_code='94')

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == {'75', '77', '78', '91', '92', '93', '94', '95'}

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
