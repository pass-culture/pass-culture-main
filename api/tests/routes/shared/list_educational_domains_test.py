import pytest

from pcapi.core.educational import factories as educational_factories


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_list_educational_domains(self, client):
        # given
        domain1 = educational_factories.EducationalDomainFactory(name="aomain1")
        domain2 = educational_factories.EducationalDomainFactory(name="bomain2")
        domain3 = educational_factories.EducationalDomainFactory(name="bomain3")

        # when
        response = client.get("/collective/educational-domains")

        # then
        assert response.status_code == 200
        assert response.json == [
            {"id": domain1.id, "name": "aomain1"},
            {"id": domain2.id, "name": "bomain2"},
            {"id": domain3.id, "name": "bomain3"},
        ]
