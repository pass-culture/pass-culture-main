import pytest
from unittest.mock import patch

from domain.departments import get_departement_codes_from_user, is_postal_code_eligible
from tests.model_creators.generic_creators import create_user


class GetDepartementCodesFromUser:
    def test_departments_mapping_with_known_department_code(self):
        # given
        user = create_user(departement_code='973')

        # when
        with patch('domain.departments.DEPARTEMENT_CODE_VISIBILITY', {'08': ['02', '08'], '97': ['971', '97']}):
            departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == set(['971', '97'])

    def test_departments_mapping_with_unknown_department_code(self):
        # given
        user = create_user(departement_code='32')

        # when
        with patch('domain.departments.DEPARTEMENT_CODE_VISIBILITY', {'08': ['02', '08'], '97': ['971', '97']}):
            departement_codes = get_departement_codes_from_user(user)

        # then
        assert departement_codes == ['32']


class IsPostalCodeEligibleTest:
    @pytest.mark.parametrize('postal_code', [
        '34000',
        '34898',
        '97340'
    ])
    def test_returns_true_for_eligible_departments(self, postal_code):
        # when
        is_eligible = is_postal_code_eligible(postal_code)

        # then
        assert is_eligible

    @pytest.mark.parametrize('postal_code', [
        '36000',
        '36034',
        '97400'
    ])
    def test_returns_false_for_non_eligible_departments(self, postal_code):
        # when
        is_eligible = is_postal_code_eligible(postal_code)

        # then
        assert not is_eligible
