import pytest

from pcapi.core.offerers.factories import VenueLabelFactory
from pcapi.core.users.factories import ProFactory


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_not_authenticated(self, client):
        # When
        response = client.get("/venue-labels")

        # then
        assert response.status_code == 401


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_the_user_is_authenticated(self, client):
        # Given
        pro = ProFactory()
        venue_label_1 = VenueLabelFactory(label="Maison des illustres")
        venue_label_2 = VenueLabelFactory(label="Monuments historiques")

        # When
        response = client.with_session_auth(pro.email).get("/venue-labels")

        # then
        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json == [
            {"id": venue_label_1.id, "label": venue_label_1.label},
            {"id": venue_label_2.id, "label": venue_label_2.label},
        ]
