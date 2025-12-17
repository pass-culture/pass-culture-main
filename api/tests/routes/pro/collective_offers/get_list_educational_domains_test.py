import pytest

from pcapi.core.educational import factories as educational_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_list_educational_domains(self, client):
        program_1 = educational_factories.NationalProgramFactory(name="program 1")
        program_2 = educational_factories.NationalProgramFactory(name="program 2")
        program_3 = educational_factories.NationalProgramFactory(name="program 3", isActive=False)

        domain_1 = educational_factories.EducationalDomainFactory(name="domain 1")
        domain_1.nationalPrograms = [program_1, program_2]

        domain_2 = educational_factories.EducationalDomainFactory(name="domain 2")
        domain_2.nationalPrograms = [program_2, program_3]  # program_3 is inactive and should not appear in result

        domain_3 = educational_factories.EducationalDomainFactory(name="domain 3")

        response = client.get("/collective/educational-domains")

        assert response.status_code == 200
        assert response.json == [
            {
                "id": domain_1.id,
                "name": "domain 1",
                "nationalPrograms": [
                    {"id": program_1.id, "name": "program 1"},
                    {"id": program_2.id, "name": "program 2"},
                ],
            },
            {
                "id": domain_2.id,
                "name": "domain 2",
                "nationalPrograms": [{"id": program_2.id, "name": "program 2"}],
            },
            {"id": domain_3.id, "name": "domain 3", "nationalPrograms": []},
        ]
