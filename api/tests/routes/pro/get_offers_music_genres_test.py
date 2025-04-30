import pytest

from pcapi.core import testing
import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types(client):
    user = users_factories.UserFactory()
    client = client.with_session_auth(email=user.email)
    with testing.assert_num_queries(testing.AUTHENTICATION_QUERIES):
        response = client.get("/offers/music-types")
        assert response.status_code == 200

    assert response.json == [
        {"gtl_id": "01000000", "label": "Musique Classique", "canBeEvent": True},
        {"gtl_id": "02000000", "label": "Jazz / Blues", "canBeEvent": True},
        {"gtl_id": "03000000", "label": "Bandes originales", "canBeEvent": False},
        {"gtl_id": "04000000", "label": "Electro", "canBeEvent": True},
        {"gtl_id": "05000000", "label": "Pop", "canBeEvent": True},
        {"gtl_id": "06000000", "label": "Rock", "canBeEvent": True},
        {"gtl_id": "07000000", "label": "Metal", "canBeEvent": True},
        {"gtl_id": "08000000", "label": "Alternatif", "canBeEvent": True},
        {"gtl_id": "09000000", "label": "Variétés", "canBeEvent": True},
        {"gtl_id": "10000000", "label": "Funk / Soul / RnB / Disco", "canBeEvent": True},
        {"gtl_id": "11000000", "label": "Rap / Hip Hop", "canBeEvent": True},
        {"gtl_id": "12000000", "label": "Reggae / Ragga", "canBeEvent": True},
        {"gtl_id": "13000000", "label": "Musique du monde", "canBeEvent": True},
        {"gtl_id": "14000000", "label": "Country / Folk", "canBeEvent": True},
        {"gtl_id": "15000000", "label": "Vidéos musicales", "canBeEvent": False},
        {"gtl_id": "16000000", "label": "Compilations", "canBeEvent": False},
        {"gtl_id": "17000000", "label": "Ambiance", "canBeEvent": True},
        {"gtl_id": "18000000", "label": "Enfants", "canBeEvent": False},
        {"gtl_id": "19000000", "label": "Autre", "canBeEvent": True},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types_unauthentified_user(client):
    with testing.assert_num_queries(0):
        response = client.get("/offers/music-types")
        assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}
