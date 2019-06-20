import pytest

from domain.departments import get_departement_codes_from_user
from tests.test_utils import create_user


class GetDepartementCodesFromUser:
    @pytest.mark.parametrize('user_department_code,expected_departement_codes', [
        ('08', {'02', '08', '51', '55', '59'}),
        ('25', {'21', '25', '39', '67', '68', '70', '71', '90'}),
        ('29', {'22', '35', '29', '56'}),
        ('34', {'11', '12', '13', '30', '31', '34', '48', '66', '81', '84'}),
        ('35', {'22', '29', '35', '44', '49', '50', '53', '56'}),
        ('58', {'03', '18', '21', '45', '58', '71', '89'}),
        ('67', {'54', '55', '57', '67', '68', '88'}),
        ('71', {'01', '03', '21', '39', '42', '58', '69', '71'}),
        ('84', {'04', '07', '13', '26', '30', '83', '84'}),
        ('93', {'75', '77', '78', '91', '92', '93', '94', '95'}),
        ('94', {'75', '77', '78', '91', '92', '93', '94', '95'}),
        ('97', {'97', '971', '972', '973'}),
        ('973', {'97', '971', '972', '973'}),
        ('01', {'01'}),
    ])
    def test_departments_mapping(self, user_department_code, expected_departement_codes):
        # given
        user = create_user(departement_code=user_department_code)

        # when
        departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == expected_departement_codes
