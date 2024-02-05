import pytest

from pcapi.core.educational import factories
import pcapi.core.educational.api.national_program as api
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


class GetNationalProgramFromDomainsTest:
    def test_get_programs(self):
        program = factories.NationalProgramFactory()
        domain_id = factories.EducationalDomainFactory(nationalPrograms=[program]).id

        with assert_num_queries(1):
            programs = api.get_national_programs_from_domains([domain_id])

            assert len(programs) == 1
            assert programs[0].id == program.id

    def test_no_programs(self):
        domain_id = factories.EducationalDomainFactory(nationalPrograms=[]).id

        with assert_num_queries(1):
            programs = api.get_national_programs_from_domains([domain_id])
            assert not programs

    def test_no_domains(self):
        with assert_num_queries(1):
            programs = api.get_national_programs_from_domains([])
            assert not programs

    def test_unknown_domain(self):
        with assert_num_queries(1):
            programs = api.get_national_programs_from_domains([-1])
            assert not programs
