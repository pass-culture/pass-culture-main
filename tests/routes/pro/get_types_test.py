import pytest

from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


class Returns401Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_anonymous(self, app):
        # when
        response = TestClient(app.test_client()).get("/types")

        # then
        assert response.status_code == 401


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged(self, app):
        # given
        users_factories.ProFactory(email="test@email.com")

        # when
        response = TestClient(app.test_client()).with_auth("test@email.com").get("/types")
        types = response.json

        # then
        assert response.status_code == 200
        types_values = [type["value"] for type in types]
        assert "ThingType.ACTIVATION" not in types_values
        assert "EventType.ACTIVATION" not in types_values
        assert "ThingType.OEUVRE_ART" in types_values
        assert "ThingType.INSTRUMENT" in types_values
        assert "ThingType.LIVRE_AUDIO" in types_values

    @pytest.mark.usefixtures("db_session")
    def when_user_is_admin(self, app):
        # given
        users_factories.AdminFactory(email="pctest.admin93.0@example.com")

        # when
        response = TestClient(app.test_client()).with_auth("pctest.admin93.0@example.com").get("/types")
        types = response.json

        # then
        assert response.status_code == 200
        types_values = [type["value"] for type in types]
        assert "ThingType.ACTIVATION" not in types_values
        assert "EventType.ACTIVATION" not in types_values

    @pytest.mark.usefixtures("db_session")
    def when_user_returns_types_labels(self, app):
        # given
        users_factories.ProFactory(email="test@email.com")

        # when
        response = TestClient(app.test_client()).with_auth("test@email.com").get("/types")
        types = response.json

        # then
        assert response.status_code == 200
        pro_labels = [type["proLabel"] for type in types]
        app_labels = [type["appLabel"] for type in types]

        assert "Livres papier ou numérique, abonnements lecture" in pro_labels
        assert "Conférences, rencontres et découverte des métiers" in pro_labels
        assert "Musées, galeries, patrimoine - entrées libres, abonnements" in pro_labels
        assert "Pratique artistique - séances d'essai et stages ponctuels" in pro_labels
        assert "Livres papier ou numérique, abonnements lecture" in pro_labels
        assert "Livres audio numériques" in pro_labels
        assert "Vente et location d’instruments de musique" in pro_labels
        assert "Vente d'œuvres d'art" in pro_labels

        assert "Œuvre d’art" in app_labels
        assert "Instrument de musique" in app_labels
        assert "Livre ou carte lecture" in app_labels
