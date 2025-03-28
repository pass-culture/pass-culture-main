from pcapi.core.educational import academies


class GetAcademyFromDepartmentTest:
    def test_get_academy_from_department(self) -> None:
        academy = academies.get_academy_from_department("988")
        assert academy == "Nouvelle-Calédonie"

        academy = academies.get_academy_from_department(None)
        assert academy is None
