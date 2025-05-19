from typing import Any

import pytest

import pcapi.core.users.factories as users_factories
from pcapi.core import testing


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_educational_partners(self, client: Any) -> None:
        pro_user = users_factories.ProFactory()

        client = client.with_session_auth(pro_user.email)
        queries = testing.AUTHENTICATION_QUERIES
        with testing.assert_num_queries(queries):
            response = client.get("/cultural-partners")
            assert response.status_code == 200

        assert response.json == {
            "partners": [
                {
                    "id": 128029,
                    "libelle": "Musée de St Paul Les trois Châteaux : Le musat Musée d'Archéologie Tricastine",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                },
                {
                    "id": 128028,
                    "libelle": "Fête du livre jeunesse de St Paul les trois Châteaux",
                    "communeLibelle": "SAINT-PAUL-TROIS-CHATEAUX",
                    "regionLibelle": "AUVERGNE-RHÔNE-ALPES",
                },
            ]
        }


class Return401Test:
    def test_get_educational_partners_no_user_login(self, client: Any) -> None:
        with testing.assert_num_queries(0):
            response = client.get("/cultural-partners")
            assert response.status_code == 401
