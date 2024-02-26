import pytest

import pcapi.core.users.factories as users_factories


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types(client):
    # Given
    user = users_factories.UserFactory()
    # When
    response = client.with_session_auth(email=user.email).get("/offers/music-types/all")
    assert response.status_code == 200
    assert response.json == [
        {"gtl_id": "01000000", "label": "Musique Classique"},
        {"gtl_id": "02000000", "label": "Jazz / Blues"},
        {"gtl_id": "03000000", "label": "Bandes originales"},
        {"gtl_id": "04000000", "label": "Electro"},
        {"gtl_id": "05000000", "label": "Pop"},
        {"gtl_id": "06000000", "label": "Rock"},
        {"gtl_id": "07000000", "label": "Metal"},
        {"gtl_id": "08000000", "label": "Alternatif"},
        {"gtl_id": "09000000", "label": "Variétés"},
        {"gtl_id": "10000000", "label": "Funk / Soul / RnB / Disco"},
        {"gtl_id": "11000000", "label": "Rap/ Hip Hop"},
        {"gtl_id": "12000000", "label": "Reggae / Ragga"},
        {"gtl_id": "13000000", "label": "Musique du monde"},
        {"gtl_id": "14000000", "label": "Country / Folk"},
        {"gtl_id": "15000000", "label": "Vidéos musicales"},
        {"gtl_id": "16000000", "label": "Compilations"},
        {"gtl_id": "17000000", "label": "Ambiance"},
        {"gtl_id": "18000000", "label": "Enfants"},
        {"gtl_id": "19000000", "label": "Autre"},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_event_music_types(client):
    # Given
    user = users_factories.UserFactory()
    # When
    response = client.with_session_auth(email=user.email).get("/offers/music-types/event")
    assert response.status_code == 200
    assert response.json == [
        {"gtl_id": "01000000", "label": "Musique Classique"},
        {"gtl_id": "02000000", "label": "Jazz / Blues"},
        {"gtl_id": "04000000", "label": "Electro"},
        {"gtl_id": "05000000", "label": "Pop"},
        {"gtl_id": "06000000", "label": "Rock"},
        {"gtl_id": "07000000", "label": "Metal"},
        {"gtl_id": "08000000", "label": "Alternatif"},
        {"gtl_id": "09000000", "label": "Variétés"},
        {"gtl_id": "10000000", "label": "Funk / Soul / RnB / Disco"},
        {"gtl_id": "11000000", "label": "Rap/ Hip Hop"},
        {"gtl_id": "12000000", "label": "Reggae / Ragga"},
        {"gtl_id": "13000000", "label": "Musique du monde"},
        {"gtl_id": "14000000", "label": "Country / Folk"},
        {"gtl_id": "17000000", "label": "Ambiance"},
        {"gtl_id": "19000000", "label": "Autre"},
    ]


@pytest.mark.usefixtures("db_session")
def test_get_all_music_types_unauthentified_user(client):
    response = client.get("/offers/music-types/all")
    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}


@pytest.mark.usefixtures("db_session")
def test_get_event_music_types_unauthentified_user(client):
    response = client.get("/offers/music-types/event")
    assert response.status_code == 401
    assert response.json == {"global": ["Authentification nécessaire"]}
