import pytest

from domain.departments import get_departement_codes_from_user
from unittest.mock import patch
from tests.test_utils import create_user


class GetDepartementCodesFromUser:
    def test_departments_mapping(self):
        # given
        user = create_user(departement_code='97')

        # when
        with patch('domain.departments.DEPARTEMENT_CODE_VISIBILITY', {'08': ['02', '08'], '97': ['971', '97']}):
            departement_codes = get_departement_codes_from_user(user)

        # then
        assert set(departement_codes) == set(['971', '97'])
