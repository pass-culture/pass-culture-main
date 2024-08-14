from typing import Any

import pytest

from pcapi.core.testing import assert_num_queries
import pcapi.core.users.factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class Return200Test:
    def test_get_educational_partners(self, client: Any) -> None:
        # Given
        pro_user = users_factories.ProFactory()

        client.with_session_auth(pro_user.email)
        with assert_num_queries(2):  # user + session
            response = client.get("/cultural-partners")
            assert response.status_code == 200

        # Then
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
        # Given

        with assert_num_queries(0):
            response = client.get("/cultural-partners")
            assert response.status_code == 401
